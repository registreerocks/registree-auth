# Registree API Authorization

## Installation

## Usage

```python
from flask import Flask

from registree_auth import requires_auth, requires_scope
app = Flask(__name__)

@app.route('/')
@requires_auth
@requires_scope('admin')
def display():
  return "This is protected information!"

if __name__=='__main__':
  app.run()
```

Environment variables:

| Variable | Type | Default | Description |
| -- | -- | -- | -- |
| AUTH0_DOMAIN | String (URL) | None | Auth0 account URL |
| API_IDENTIFIER | String (URL) | None | Auth0 API identifier |
| ALGORITHMS | String (Array) | "['RS256']" | JWT signing algorithm set in Auth0 |
| UPORT_ISSUER | String (Public key) | None | Public key of credential issuer |
| UPORT_VALIDATION_URL | String (URL) | None | URL to UPort credential validation service |
| VALIDATION | Bool (0/1) | 1 | Possibility to switch of authorization. Must only be used for data porting. |


## Example
Export necessary environment variables:
```sh
# Auth0 account domain and API identifier
$ export AUTH0_DOMAIN=SUBDOMAIN.eu.auth0.com
$ export API_IDENTIFIER=https://url.of/your/api
```

Depending on the token you are using, you may also want to export the UPort variables:
```sh
# Uport credential issuer and validation service URL
$ export UPORT_ISSUER=PUBLIC_KEY
$ export UPORT_VALIDATION_URL=https://url.of/validation/service
```

Install dependencies:
```sh
$ pip install -r requirements.txt
```

Start the example server:
```sh
$ python example.py
```

Request without token:
```sh
$ http localhost:5000
HTTP/1.0 401 UNAUTHORIZED
Content-Length: 65
Content-Type: application/json
Date: Wed, 22 Apr 2020 08:14:09 GMT
Server: Werkzeug/1.0.1 Python/3.7.5

{
    "ERROR": "Invalid header. Use an RS256 signed JWT Access Token"
}
```

Request with valid token:
```sh
$ http localhost:5000 'Authorization: Bearer somevalidtoken'
HTTP/1.0 200 OK
Content-Length: 30
Content-Type: text/html; charset=utf-8
Date: Wed, 22 Apr 2020 08:16:10 GMT
Server: Werkzeug/1.0.1 Python/3.7.5

This is protected information!
```

## Development

Install the package locally via 
```
$ pip install .
```