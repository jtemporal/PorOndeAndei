import configparser
import os
import json

from functools import wraps
from urllib.request import urlopen
from flask import request, _request_ctx_stack, abort, Response
from jose import jwt

env = os.getenv("ENV", "dev")

if env == "dev":
    config = configparser.ConfigParser()
    config.read(".config")
    config = config["AUTH0"]
else:
    config = {
        "DOMAIN": os.getenv("DOMAIN", "your.domain.com"),
        "API_AUDIENCE": os.getenv("API_AUDIENCE", "your.audience.com"),
        "ALGORITHMS": os.getenv("ALGORITHMS", "RS256"),
    }


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token():
    """Obtains the Access Token from the Authorization Header"""

    # Get the authorization header
    authorization_header = request.headers.get("Authorization", None)

    # Raise an error if no Authorization error is found
    if not authorization_header:
        payload = {
            "code": "authorization_header_missing",
            "description": "Authorization header is expected",
        }
        raise AuthError(payload, 401)

    authorization_header_parts = authorization_header.split()

    # We are expecting the Authorization header to contain a Bearer token
    if authorization_header_parts[0].lower() != "bearer":
        payload = {
            "code": "invalid_header",
            "description": "Authorization header must be a Bearer token",
        }
        raise AuthError(payload, 401)

    # The Authorization header is prefixed with Bearer,
    # but does not contain the actual token
    elif len(authorization_header_parts) == 1:
        payload = {"code": "invalid_header", "description": "Token not found"}
        raise AuthError(payload, 401)

    # We only expect 2 parts, "Bearer" and the access token
    elif len(authorization_header_parts) > 2:
        payload = {
            "code": "invalid_header",
            "description": "Authorization header must be a valid Bearer token",
        }
        raise AuthError(payload, 401)

    # If all checks out, we return the access token
    return authorization_header_parts[1]


def validate_token(token):
    """Validates an Access Token"""
    # Let's find our publicly available public keys,
    # which we'll use to validate the token's signature
    jsonurl = urlopen("https://" + config["DOMAIN"] + "/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())

    # We will parse the token and get the header for later use
    unverified_header = jwt.get_unverified_header(token)

    # Check if the token has a key ID
    if "kid" not in unverified_header:
        payload = {
            "code": "missing_kid",
            "description": "No kid found in token"
        }
        raise AuthError(payload, 401)

    try:
        # Check if we have a key with the key ID specified
        # from the header available in our list of public keys
        rsa_key = next(
            key for key in jwks["keys"]
            if key["kid"] == unverified_header["kid"]
        )

        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=config["ALGORITHMS"],
                audience=config["API_AUDIENCE"],
                issuer="https://" + config["DOMAIN"] + "/",
            )
            _request_ctx_stack.top.current_user = payload

        # The token is not valid if the expiry date is in the past
        except jwt.ExpiredSignatureError:
            raise AuthError(
                {"code": "token_expired", "description": "Token is expired"},
                401
            )

        # The token should be issued by our Auth0 tenant,
        # and to be used with our API (Audience)
        except jwt.JWTClaimsError:
            payload = {
                "code": "invalid_claims",
                "description":
                    "Incorrect claims, please check the audience and issuer",
            }
            raise AuthError(payload, 401)

        # The token's signature is invalid
        except jwt.JWTError:
            payload = {
                "code": "invalid_signature",
                "description": "The signature is not valid",
            }
            raise AuthError(payload, 401)

        # Something went wrong parsing the JWT
        except Exception:
            payload = {
                "code": "invalid_header",
                "description": "Unable to parse authentication token.",
            }
            raise AuthError(payload, 401)

    except StopIteration:
        # We did not find the key with the ID specified in the token's header
        # in the list of available public keys for our Auth0 tenant.
        payload = {
            "code": "invalid_header",
            "description": "No valid public key found to validate signature.",
        }
        raise AuthError(payload, 401)


def requires_auth(f):
    """Determines if there is a valid Access Token available"""

    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Lets get the access token from the Authorization header
            token = get_token()

            # Once we have the token, we can validate it
            validate_token(token)
        except AuthError as error:
            # Abort the request if something went wrong fetching the token
            # or validating the token.
            # We return the status from the raised error,
            # and return the error as a json response body
            return abort(Response(json.dumps(error.error), error.status_code))

        return f(*args, **kwargs)

    return decorated
