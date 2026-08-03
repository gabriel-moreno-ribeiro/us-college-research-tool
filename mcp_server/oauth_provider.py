"""
Minimal OAuth 2.0 provider for Claude.ai connector compatibility.

Claude.ai requires MCP servers to implement OAuth before connecting.
Since our actual security model is BYOK (keys in headers), this OAuth
layer is a passthrough — it auto-approves all clients and issues tokens
that always validate. No real authentication happens here.

The BYOK headers (X-College-Scorecard-Key, X-Semantic-Scholar-Key) are
what actually gate access to upstream APIs.
"""
from __future__ import annotations

import hashlib
import secrets
import time
from typing import Any

from pydantic import AnyUrl

from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationParams,
    OAuthAuthorizationServerProvider,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken


class SimpleOAuthProvider(OAuthAuthorizationServerProvider[str, str, str]):
    """In-memory OAuth provider that auto-approves everything."""

    def __init__(self) -> None:
        self._clients: dict[str, OAuthClientInformationFull] = {}
        self._auth_codes: dict[str, dict[str, Any]] = {}
        self._tokens: dict[str, dict[str, Any]] = {}

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        return self._clients.get(client_id)

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        self._clients[client_info.client_id] = client_info

    async def authorize(
        self, client: OAuthClientInformationFull, params: AuthorizationParams
    ) -> str:
        code = secrets.token_urlsafe(32)
        self._auth_codes[code] = {
            "client_id": client.client_id,
            "redirect_uri": str(params.redirect_uri),
            "code_challenge": params.code_challenge,
            "scopes": params.scopes or [],
            "created_at": time.time(),
        }
        redirect = str(params.redirect_uri)
        separator = "&" if "?" in redirect else "?"
        url = f"{redirect}{separator}code={code}"
        if params.state:
            url += f"&state={params.state}"
        return url

    async def load_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> str | None:
        if authorization_code in self._auth_codes:
            data = self._auth_codes[authorization_code]
            if data["client_id"] == client.client_id:
                return authorization_code
        return None

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> OAuthToken:
        data = self._auth_codes.pop(authorization_code, {})
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        self._tokens[access_token] = {
            "client_id": client.client_id,
            "scopes": data.get("scopes", []),
            "created_at": time.time(),
        }
        self._tokens[refresh_token] = {
            "client_id": client.client_id,
            "scopes": data.get("scopes", []),
            "created_at": time.time(),
            "is_refresh": True,
        }
        return OAuthToken(
            access_token=access_token,
            token_type="Bearer",
            expires_in=3600 * 24 * 365,
            refresh_token=refresh_token,
        )

    async def load_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: str
    ) -> str | None:
        data = self._tokens.get(refresh_token)
        if data and data.get("is_refresh") and data["client_id"] == client.client_id:
            return refresh_token
        return None

    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: str,
        scopes: list[str],
    ) -> OAuthToken:
        self._tokens.pop(refresh_token, None)
        access_token = secrets.token_urlsafe(32)
        new_refresh = secrets.token_urlsafe(32)
        self._tokens[access_token] = {
            "client_id": client.client_id,
            "scopes": scopes,
            "created_at": time.time(),
        }
        self._tokens[new_refresh] = {
            "client_id": client.client_id,
            "scopes": scopes,
            "created_at": time.time(),
            "is_refresh": True,
        }
        return OAuthToken(
            access_token=access_token,
            token_type="Bearer",
            expires_in=3600 * 24 * 365,
            refresh_token=new_refresh,
        )

    async def load_access_token(self, token: str) -> str | None:
        if token in self._tokens and not self._tokens[token].get("is_refresh"):
            return token
        return None

    async def revoke_token(self, token: str) -> None:
        self._tokens.pop(token, None)

    async def verify_access_token(self, token: str) -> AccessToken | None:
        data = self._tokens.get(token)
        if not data or data.get("is_refresh"):
            return None
        return AccessToken(
            token=token,
            client_id=data["client_id"],
            scopes=data.get("scopes", []),
            expires_at=int(data["created_at"] + 3600 * 24 * 365),
        )
