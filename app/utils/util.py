from datetime import UTC, datetime, timedelta
from functools import wraps

from flask import jsonify, request
from jose import JWTError, jwt

SECRET_KEY = "my_super_secret_key"
ALGORITHM = "HS256"


def encode_token(customer_id):
    """Generates a token valid for 1 hour."""
    payload = {
        "exp": datetime.now(UTC) + timedelta(hours=1),
        "iat": datetime.now(UTC),
        "sub": str(customer_id),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def token_required(f):
    """A decorator tool to protect specific routes."""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing. Please log in."}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            customer_id = int(payload["sub"])
        except JWTError:
            return jsonify({"message": "Token is invalid or expired."}), 401

        return f(customer_id, *args, **kwargs)

    return decorated
