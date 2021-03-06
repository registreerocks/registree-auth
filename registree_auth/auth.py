import json
from functools import wraps
from os import environ as env

from flask import _request_ctx_stack, request
from jose import jwt
from six.moves.urllib.request import Request, urlopen

AUTH0_DOMAIN = env.get("AUTH0_DOMAIN")
API_IDENTIFIER = env.get("API_IDENTIFIER")
ALGORITHMS = eval(env.get("ALGORITHMS", "['RS256']"))
UPORT_ISSUER = env.get("UPORT_ISSUER")
UPORT_VALIDATION_URL = env.get("UPORT_VALIDATION_URL")
VALIDATION = int(env.get("VALIDATION", "1")) != 0


def get_token_auth_header():
  """Obtains the access token from the Authorization Header
  """
  auth = request.headers.get("Authorization", None)
  if not auth:
    return {"ERROR": "Authorization header is expected"}, 401

  parts = auth.split()

  if parts[0].lower() != "bearer":
    return {"ERROR": "Authorization header must start with Bearer"}, 401
  elif len(parts) == 1:
    return {"ERROR": "Token not found"}, 401
  elif len(parts) > 2:
    return {"ERROR": "Authorization header must be Bearer token"}, 401

  token = parts[1]
  return token

def check_user_id(f):
  """Checks whether provided user id is equivalent to the user id stored in the token
  """
  @wraps(f)
  def decorated(*args, **kwargs):
    token = get_token_auth_header()
    unverified_claims = jwt.get_unverified_claims(token)
    if unverified_claims.get("sub") and unverified_claims.get("sub") == kwargs['id']:
      return f(*args, **kwargs)
    return {"ERROR": "Invalid user id. Method not allowed for user id " + str(kwargs['id'])}, 401
    
  return decorated


def requires_scope(*required_scopes):
  """Determines if the required scope is present in the access token
  Args:
    required_scopes (str): Scopes allowed to access the resource
  """

  def requires_scope_decorator(f):

    def wrapper(*args, **kwargs):
      token = get_token_auth_header()
      unverified_claims = jwt.get_unverified_claims(token)
      if unverified_claims.get("scope"):
        token_scopes = unverified_claims["scope"].split()
        for token_scope in token_scopes:
          if token_scope in required_scopes:
            return f(*args, **kwargs)
      elif unverified_claims.get("iss") == UPORT_ISSUER:
        return f(*args, **kwargs)
      return {"ERROR": "Invalid scope. Method not allowed for scope " + str(token_scope)}, 401

    if VALIDATION:
      return wrapper
    else: 
      return f

  return requires_scope_decorator


def requires_auth(f):
  """Determines if the access token is valid
  """
  @wraps(f)
  def decorated(*args, **kwargs):
    token = get_token_auth_header()
    jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    try:
      unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError:
      return {"ERROR": "Invalid header. Use an RS256 signed JWT Access Token"}, 401
    if unverified_header["alg"] == "HS256":
      return {"ERROR": "Invalid header. Use an RS256 signed JWT Access Token"}, 401
    elif unverified_header["alg"] == "ES256K":
      request = Request(UPORT_VALIDATION_URL, {'jwt': token, 'did': 'did:uport:' + UPORT_ISSUER}, {})
      response = urlopen(request)
      response_body = json.loads(response.read())
      if response_body.get('status') == 'SUCCESS':
        return f(*args, **kwargs)
      return {"ERROR": response_body.get('response')}, 401
    else:
      rsa_key = {}
      for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
          rsa_key = {
            "kty": key["kty"],
            "kid": key["kid"],
            "use": key["use"],
            "n": key["n"],
            "e": key["e"]
          }
      if rsa_key:
        try:
          payload = jwt.decode(
              token,
              rsa_key,
              algorithms=ALGORITHMS,
              audience=API_IDENTIFIER,
              issuer="https://"+AUTH0_DOMAIN+"/"
          )
        except jwt.ExpiredSignatureError:
          return {"ERROR": "token is expired"}, 401
        except jwt.JWTClaimsError:
          return {"ERROR": "incorrect claims, please check the audience and issuer"}, 401
        except Exception:
          return {"ERROR": "Unable to parse authentication token."}, 401

        _request_ctx_stack.top.current_user = payload
        return f(*args, **kwargs)
      return {"ERROR": "Unable to find appropriate key"}, 401
          
  if VALIDATION: 
    return decorated
  else:
    return f
