import os
from flask import Flask, redirect, request, jsonify
from oauth import OAuthClient

app = Flask(__name__)

CONFIG_PATH = os.environ.get("OAUTH_CONFIG_PATH", "/secrets/client_secret.json")
TOKEN_PATH = os.environ.get("OAUTH_TOKEN_PATH", "/data/token.json")

client = OAuthClient(CONFIG_PATH, TOKEN_PATH)


@app.route("/")
def index():
    token = client.load_token()
    if token:
        return jsonify({"status": "authenticated", "has_refresh_token": "refresh_token" in token})
    return f'<a href="/login">Login with Google</a>'


@app.route("/login")
def login():
    return redirect(client.build_auth_url())


@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Missing code parameter", 400
    token = client.exchange_code(code)
    return jsonify({"status": "authenticated", "has_refresh_token": "refresh_token" in token})


@app.route("/token")
def get_token():
    token = client.get_valid_token()
    if not token:
        return jsonify({"error": "not_authenticated"}), 401
    return jsonify({"access_token": token["access_token"], "token_type": token.get("token_type", "Bearer")})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
