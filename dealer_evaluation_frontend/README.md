# Frontend

A single page that lets you choose a product and see its price at one dealer or at all dealers. Back to the [project README](../README.md).

It is a tiny Flask app (`app.py`) that renders one template (`html/index.html`). There is no build step and no JavaScript framework; the page uses plain JavaScript and [axios](https://axios-http.com) for the HTTP calls.

## How it works

1. You open `/`. Flask renders `html/index.html` and writes two values into it, the base URLs of the APIs, taken from environment variables.
2. In the browser, the page calls the product catalogue API for the list of products.
3. When you pick a product, it asks the same API for the dealers that sell it.
4. When you pick a dealer (or **All Dealers**), it calls the dealer pricing API and shows the result in a table.

The API calls are made by the **browser**, not by the Flask app. The API documentation is in the [backend README](../dealer_evaluation_backend/README.md#api-reference).

If a call fails, the page shows a short message and writes the details to the browser console. Picking something new always clears the previous result, and a slow answer for an earlier choice cannot overwrite a newer one.

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `PROD_LIST_URL` | `http://localhost:5000` | Base URL of the product catalogue API. |
| `DEALER_DETAILS_URL` | `http://localhost:8080` | Base URL of the dealer pricing API. |

A trailing slash is optional. Both URLs are used by the visitor's browser, so they must be reachable **from the browser**:

- on one machine, `localhost` URLs are right, even with Docker Compose, because the ports are published to your machine;
- Docker service names (for example `http://products-backend:5000`) do not work, because the browser does not know them;
- once deployed to the cloud, they must be public `https://` URLs. A page served over HTTPS cannot call `http://` APIs, because the browser blocks it.

## Running it without Docker

Python 3.8 or newer. Start the two [backend services](../dealer_evaluation_backend/README.md#running-a-service-without-docker) first, then, from the repository root:

```bash
cd dealer_evaluation_frontend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python3 -m flask run -p 5001     # http://localhost:5001
```

To point it at APIs running elsewhere, set the variables first:

```bash
PROD_LIST_URL=https://products.example.com DEALER_DETAILS_URL=https://dealers.example.com python3 -m flask run -p 5001
```

On Windows PowerShell, use `$env:PROD_LIST_URL="https://products.example.com"` on its own line, and the same for the other variable.

`python3 app.py` also works. It starts the same server on port 5001 in debug mode, which reloads on code changes and should only be used on your own machine.

## Running it in Docker

```bash
docker build -t price-frontend dealer_evaluation_frontend
docker run --rm -p 5001:5001 \
  -e PROD_LIST_URL=http://localhost:5000 \
  -e DEALER_DETAILS_URL=http://localhost:8080 \
  price-frontend
```

With Compose, `docker compose up --build` in the repository root starts all three services.

## Notes

- axios is loaded from the jsDelivr CDN (a pinned version), so the browser needs internet access. To work offline, download that file, serve it yourself (for example from a `static/` folder) and change the `<script src>` to match.
- Product and dealer names are URL-encoded before they are put into a request, and API data is inserted into the page as text, never as HTML.
