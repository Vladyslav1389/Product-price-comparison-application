# Deploying to IBM Cloud Code Engine

This guide deploys the three services as three separate Code Engine applications, each with its own public `https://` URL. Code Engine builds the container images itself from this repository's Dockerfiles, so you do not need Docker on your machine. Back to the [project README](../README.md).

> **Status:** the commands below follow IBM's documentation but have **not yet been run end-to-end by the author**. Last verified: _not yet_. If a step fails, `ibmcloud ce application create --help` lists the flags your CLI version supports.

## Before you start

**You need an IBM Cloud account.** IBM describes its free account as a Pay-as-you-go account: payment details are required at sign-up, and you are charged only when you use billable services. IBM also lists a USD 200 credit, valid for 30 days, for new accounts, and a free tier for Code Engine. Check the current terms at [ibm.com/products/cloud/free](https://www.ibm.com/products/cloud/free) and [ibm.com/products/code-engine/pricing](https://www.ibm.com/products/code-engine/pricing) before you start. The [clean-up](#clean-up) section at the end removes everything this guide creates.

**Where `SN_ICR_NAMESPACE` and `icr-secret` went.** The original IBM exercise ran inside the Skills Network lab environment, which provides a variable called `SN_ICR_NAMESPACE` and a registry secret called `icr-secret`. They are not part of this repository, and they do not exist outside that environment, so this guide does not use them. By default Code Engine looks after the image registry for you. If you want to choose the registry namespace yourself, see [Optional: your own registry namespace](#optional-your-own-registry-namespace).

**Tools.** Install the [IBM Cloud CLI](https://cloud.ibm.com/docs/cli?topic=cli-install-ibmcloud-cli), then add the Code Engine plugin:

```bash
ibmcloud plugin install code-engine
```

## 1. Log in and create a project

A Code Engine *project* groups the applications and holds their shared settings.

```bash
ibmcloud login                    # add --sso if your organisation uses single sign-on
ibmcloud target -g Default        # your resource group; "Default" exists in new accounts
ibmcloud ce project create --name price-comparison
ibmcloud ce project select --name price-comparison
```

## 2. Deploy the two APIs

Each command takes the source from this repository on GitHub, builds the image from the `Dockerfile` in the given folder, and starts the application. `--port` must match the port the service listens on. The first build takes a few minutes. Code Engine builds the repository's default branch, and the repository must be public. If you forked it, use your fork's URL instead.

```bash
ibmcloud ce application create --name products-api \
  --build-source https://github.com/Vladyslav1389/Product-price-comparison-application \
  --build-context-dir dealer_evaluation_backend/products_list \
  --build-strategy dockerfile \
  --port 5000

ibmcloud ce application create --name dealers-api \
  --build-source https://github.com/Vladyslav1389/Product-price-comparison-application \
  --build-context-dir dealer_evaluation_backend/dealer_details \
  --build-strategy dockerfile \
  --port 8080
```

Because no `--image` is given, Code Engine chooses where to store the built image and creates a registry secret named `ce-auto-icr-private-<region>` for it. If the build fails with a registry, namespace or permission error, use the [optional section](#optional-your-own-registry-namespace) below.

Now read the public URL of each API and check that it answers:

```bash
PRODUCTS_URL=$(ibmcloud ce application get --name products-api --output url)
DEALERS_URL=$(ibmcloud ce application get --name dealers-api --output url)

curl "$PRODUCTS_URL/products"
curl "$DEALERS_URL/allprice/Laptop"
```

You should see `{"products":["Headphones","Laptop","Mouse","Printer"]}` and the three laptop prices. If the output of `application get --output url` contains more than a URL, copy the `URL:` line from `ibmcloud ce application get --name products-api` instead.

## 3. Deploy the frontend

The frontend needs the URLs of the two APIs, because the visitor's browser calls them directly. They are passed as environment variables, so nothing in the source has to be edited:

```bash
ibmcloud ce application create --name price-frontend \
  --build-source https://github.com/Vladyslav1389/Product-price-comparison-application \
  --build-context-dir dealer_evaluation_frontend \
  --build-strategy dockerfile \
  --port 5001 \
  --env PROD_LIST_URL="$PRODUCTS_URL" \
  --env DEALER_DETAILS_URL="$DEALERS_URL"

ibmcloud ce application get --name price-frontend --output url
```

Open the printed URL in a browser, choose **Laptop** and then **All Dealers**: you should see the same table as in the [screenshot](screenshot.png).

The URLs must be the public `https://` ones. If you ever re-create an API (it gets a new URL), update the frontend:

```bash
ibmcloud ce application update --name price-frontend \
  --env PROD_LIST_URL="$PRODUCTS_URL" \
  --env DEALER_DETAILS_URL="$DEALERS_URL"
```

## Things to know

- **Cold starts.** By default Code Engine scales an idle application down to zero, so the first request after a quiet period can take several seconds. This also keeps the cost down.
- **The APIs are public.** Anyone with the URL can call them. The data is demo data and the APIs are read-only, but there is no authentication.
- **The page and the APIs have different addresses.** That works because both APIs allow cross-origin requests.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| The CLI says `ce` is not a registered command | The plugin is missing: `ibmcloud plugin install code-engine`. |
| The build fails | `ibmcloud ce buildrun list`, then `ibmcloud ce buildrun logs --buildrun <name>` for the build log. For a registry or namespace error, see the optional section below. |
| The application never becomes ready | `ibmcloud ce application logs --application products-api` and `ibmcloud ce application events --application products-api`. Check that `--port` is 5000, 8080 or 5001 for the matching service. |
| The page loads but the dropdown is empty | The frontend was started with the wrong URLs. Open the browser's developer tools and look at the failed requests. The URLs must be `https://` and must open in a browser on their own. |
| The very first request is slow | Cold start; try again. |

## Optional: your own registry namespace

Use this if the automatic registry setup does not work in your account, or if you want to control where the images are stored. The original exercise used this approach, which is where `SN_ICR_NAMESPACE` and `icr-secret` came from.

1. Add the Container Registry plugin and create a namespace. A namespace name must be unique across all IBM Cloud accounts in the same region (4 to 30 lowercase letters, numbers, hyphens or underscores), so choose your own:

   ```bash
   ibmcloud plugin install container-registry
   ibmcloud cr region-set us-south   # use the region of your Code Engine project
   ibmcloud cr region                # prints the registry domain for that region, e.g. us.icr.io
   ibmcloud cr namespace-add my-unique-namespace
   ```

2. Create an API key and a Code Engine registry secret from it. Keep the key file **outside** the repository, and delete it afterwards:

   ```bash
   ibmcloud iam api-key-create price-comparison-icr -d "Code Engine image access" --file ~/price-comparison-icr-key.json
   ```

   Copy the `apikey` value from that file, then:

   ```bash
   ibmcloud ce secret create --format registry --name icr-secret \
     --server us.icr.io --username iamapikey --password "<your API key>"
   ```

   `--server` must be the registry domain that `ibmcloud cr region` printed (`us.icr.io` in the example), and the same domain goes into the `--image` value in the next step.

3. Add the image location and the secret to each `application create` command, for example:

   ```bash
   ibmcloud ce application create --name products-api \
     --build-source https://github.com/Vladyslav1389/Product-price-comparison-application \
     --build-context-dir dealer_evaluation_backend/products_list \
     --build-strategy dockerfile \
     --image us.icr.io/my-unique-namespace/products-api \
     --registry-secret icr-secret \
     --port 5000
   ```

   Use `.../dealers-api` and `.../price-frontend` for the other two.

## Clean-up

Delete the applications, or the whole project, when you are done so that nothing keeps running or accumulating cost:

```bash
ibmcloud ce application delete --name price-frontend --force
ibmcloud ce application delete --name dealers-api --force
ibmcloud ce application delete --name products-api --force
ibmcloud ce project delete --name price-comparison
```

If you used your own registry namespace, remove it too (`ibmcloud cr namespace-rm my-unique-namespace`) and delete the API key in the IBM Cloud console under **Manage > Access (IAM) > API keys**.
