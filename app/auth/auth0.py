# import http.client

# async def get_token():
#     conn = http.client.HTTPSConnection("romanpidlipskiy.eu.auth0.com")

#     payload = "{\"client_id\":\"56QPy9u0JYbVxixTV0WrIqS9sk9xEvdy\",\"client_secret\":\"CT26BTye3P9tOoFMwJekD8YflYibbNdr42eNnHS4OSlmcqCJq7p7rMQLzvy2hE-8\",\"audience\":\"https://testauth\",\"grant_type\":\"client_credentials\"}"

#     headers = { 'content-type': "application/json" }

#     conn.request("POST", "/oauth/token", payload, headers)

#     res = conn.getresponse()
#     data = res.read()


#     return data.decode("utf-8")

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.auth_schemas import TokenData
from typing import Optional
from app.core.config import Settings
from jose import jwt


settings = Settings()


def decode_token(token: str):
    try:
        payload = jwt.decode(token, key=settings.auth0_secret_key, algorithms=[
                             settings.auth0_algorithm], audience=settings.auth0_audience, issuer=settings.auth0_issuer)
        return payload
    except:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )


http_bearer = HTTPBearer()
