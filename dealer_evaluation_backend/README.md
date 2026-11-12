# Backend services

Two small, independent HTTP APIs. Neither calls the other; the browser (see the [frontend](../dealer_evaluation_frontend/README.md)) calls both. Back to the [project README](../README.md).

| Service | Folder | Stack | Default port | Data file |
| --- | --- | --- | --- | --- |
| Product catalogue | `products_list/` | Python, Flask | 5000 | `products.json` |
| Dealer pricing | `dealer_details/` | Node.js, Express | 8080 | `utils/dealers.json` |

Both services send CORS headers that allow any origin, so a page served from another host (or port) can call them.

## API reference

The examples assume the services run locally on their default ports. Product and dealer names are case-sensitive, and names containing spaces must be URL-encoded (`Tech City` becomes `Tech%20City`).

All responses are JSON with status 200, including the "not found" cases, which are reported in a `message` field. Clients should therefore check which key is present.

### Product catalogue (port 5000)

#### `GET /products`

Lists all product names.

```bash
curl http://localhost:5000/products
```

```json
{"products":["Headphones","Laptop","Mouse","Printer"]}
```

#### `GET /getdealers/<product>`

Lists the dealers that sell a product.

```bash
curl http://localhost:5000/getdealers/Laptop
```

```json
{"dealers":["GH Computers","Tech City","Ez PC"]}
```

For an unknown product:

```json
{"message":"Could not find dealers for this product"}
```

### Dealer pricing (port 8080)

#### `GET /price/<dealer>/<product>`

The price of one product at one dealer.

```bash
curl http://localhost:8080/price/Tech%20City/Laptop
```

```json
{"message":"Laptop costs $850 at Tech City"}
```

If the dealer exists but does not sell the product, or the dealer is unknown:

```json
{"message":"Laptop is not available with Binglee"}
```

```json
{"message":"The product is not available with this dealer"}
```

#### `GET /allprice/<product>`

The price of a product at every dealer that sells it, in the order the dealers appear in `dealers.json`.

```bash
curl http://localhost:8080/allprice/Headphones
```

```json
{"prices":[{"key":"Binglee","value":"$30"},{"key":"DXC Electronics","value":"$20"},{"key":"Bobay","value":"$20"}]}
```

If no dealer sells the product:

```json
{"message":"The product is not available with this dealer"}
```

## Running a service without Docker

Run the commands from the repository root. Use a separate terminal for each service.

### `products_list` (Python 3.8 or newer)

```bash
cd dealer_evaluation_backend/products_list
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python3 -m flask run             # http://localhost:5000
```

`flask run` listens on port 5000 by default. Use `-p` to pick another port, for example `python3 -m flask run -p 5050`.

### `dealer_details` (Node.js 18 or newer)

```bash
cd dealer_evaluation_backend/dealer_details
npm ci
npm start                        # http://localhost:8080
```

Set `PORT` to listen elsewhere, for example `PORT=9090 npm start`. On Windows PowerShell: `$env:PORT=9090; npm start`.

## Running a single service in Docker

Each service has its own `Dockerfile`, with its own folder as the build context. Compose in the repository root does the same for all three services; this is only useful for one service on its own.

```bash
docker build -t products-list dealer_evaluation_backend/products_list
docker run --rm -p 5000:5000 products-list

docker build -t dealer-details dealer_evaluation_backend/dealer_details
docker run --rm -p 8080:8080 dealer-details
```

## Changing the data

Both files must agree. A dealer appears in two places, and the names must match exactly, including case and spacing.

`products_list/products.json` says which dealers sell each product:

```json
{ "product": "Mouse", "Dealers": ["DXC Electronics", "Tech City"] }
```

`dealer_details/utils/dealers.json` holds each dealer's prices:

```json
{ "Dealer": "Tech City", "products": { "Mouse": "$20", "Laptop": "$850" } }
```

To add a product, add an entry to `products.json` and a price for it under each listed dealer in `dealers.json`. To add a dealer, add it to `dealers.json` and to the `Dealers` list of each product it sells.

`products.json` is read on every request, so a change is picked up immediately. `dealers.json` is loaded once when the server starts, so restart `dealer_details` (or rebuild the Docker image) after editing it.

## Not production-ready

These services are a demo: they use the Flask development server and plain Express, they have no authentication or rate limiting, CORS allows every origin, and the data is read from static files. See the [known limitations](../README.md#known-limitations).
