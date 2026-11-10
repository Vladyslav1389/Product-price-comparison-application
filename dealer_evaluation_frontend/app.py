import os

from flask import Flask, render_template
from flask_cors import CORS

# template_folder='html' keeps the existing folder name instead of renaming
# it to Flask's default "templates" directory.
app = Flask(__name__, template_folder='html')
CORS(app)


def _base_url(env_name, default):
  # The page builds URLs as base + "products", so the base must end with "/".
  # Normalising here means "https://host" and "https://host/" both work.
  return os.environ.get(env_name, default).rstrip("/") + "/"


# These URLs are rendered into the page and called by the *browser*, so they
# must be reachable from the user's machine (not internal Docker hostnames).
# Defaults match docker-compose.yml; override them when deploying to the cloud.
PROD_LIST_URL = _base_url("PROD_LIST_URL", "http://localhost:5000")
DEALER_DETAILS_URL = _base_url("DEALER_DETAILS_URL", "http://localhost:8080")


@app.route("/")
def getHomePage():
  return render_template(
    "index.html",
    prod_url=PROD_LIST_URL,
    dealer_url=DEALER_DETAILS_URL,
  )


if __name__ == "__main__":
    # Local development only: binds to 127.0.0.1 so the debugger is not
    # exposed to the network. In Docker the app is started with `flask run`.
    app.run(port=5001, debug=True)
