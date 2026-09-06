import time
import httpx

from core.config import settings

_token: str | None = None
_token_expires_at: float = 0


async def get_access_token() -> str:
    global _token, _token_expires_at
    if _token and time.time() < _token_expires_at - 60:
        return _token
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://{settings.SHOPIFY_SHOP_DOMAIN}.myshopify.com/admin/oauth/access_token",
            data={
                "grant_type": "client_credentials",
                "client_id": settings.SHOPIFY_CLIENT_ID,
                "client_secret": settings.SHOPIFY_CLIENT_SECRET,
            },
        )
        resp.raise_for_status()
        body = resp.json()
    _token = body["access_token"]
    _token_expires_at = time.time() + body["expires_in"]
    return _token


async def graphql(query: str, variables: dict | None = None) -> dict:
    token = await get_access_token()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://{settings.SHOPIFY_SHOP_DOMAIN}.myshopify.com/admin/api/2026-07/graphql.json",
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Access-Token": token,
            },
            json={"query": query, "variables": variables or {}},
        )
        resp.raise_for_status()
        return resp.json()