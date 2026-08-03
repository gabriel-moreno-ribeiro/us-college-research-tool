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

import secrets
import time
from dataclasses import dataclass, field

from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationParams,
    OAuthAuthorizationServerProvider,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken


@dataclass
class AuthCode:
    """Authorization code with metadata the SDK token handler needs."""
    code: str
    client_id: str
    redirect_uri: str
    redirect_uri_provided_explicitly: bool
    code_challenge: str
    scopes: list[str]
    expires_at: float


@dataclass
class RefreshTokenData:
    """Refresh token with metadata the SDK token handler needs."""
    token: str
    client_id: str
    scopes: list[str]
    expires_at: float


class SimpleOAuthProvider(OAuthAuthorizationServerProvider[AuthCode, RefreshTokenData, AccessToken]):
    """In-memory OAuth provider that auto-approves everything."""

    def __init__(self) -> None:
        self._clients: dict[str, OAuthClientInformationFull] = {}
        self._auth_codes: dict[str, AuthCode] = {}
        self._refresh_tokens: dict[str, RefreshTokenData] = {}
        self._access_tokens: dict[str, AccessToken] = {}

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        return self._clients.get(client_id)

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        self._clients[client_info.client_id] = client_info

    async def authorize(
        self, client: OAuthClientInformationFull, params: AuthorizationParams
    ) -> str:
        code = secrets.token_urlsafe(32)
        self._auth_codes[code] = AuthCode(
            code=code,
            client_id=client.client_id,
            redirect_uri=str(params.redirect_uri),
            redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
            code_challenge=params.code_challenge,
            scopes=params.scopes or [],
            expires_at=time.time() + 600,
        )
        redirect = str(params.redirect_uri)
        separator = "&" if "?" in redirect else "?"
        url = f"{redirect}{separator}code={code}"
        if params.state:
            url += f"&state={params.state}"
        return url

    async def load_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> AuthCode | None:
        auth_code = self._auth_codes.get(authorization_code)
        if auth_code and auth_code.client_id == client.client_id:
            return auth_code
        return None

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: AuthCode
    ) -> OAuthToken:
        self._auth_codes.pop(authorization_code.code, None)
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        self._access_tokens[access_token] = AccessToken(
            token=access_token,
            client_id=client.client_id,
            scopes=authorization_code.scopes,
            expires_at=int(time.time()) + 3600 * 24 * 365,
        )
        self._refresh_tokens[refresh_token] = RefreshTokenData(
            token=refresh_token,
            client_id=client.client_id,
            scopes=authorization_code.scopes,
            expires_at=time.time() + 3600 * 24 * 365,
        )
        return OAuthToken(
            access_token=access_token,
            token_type="Bearer",
            expires_in=3600 * 24 * 365,
            refresh_token=refresh_token,
        )

    async def load_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: str
    ) -> RefreshTokenData | None:
        data = self._refresh_tokens.get(refresh_token)
        if data and data.client_id == client.client_id:
            return data
        return None

    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshTokenData,
        scopes: list[str],
    ) -> OAuthToken:
        self._refresh_tokens.pop(refresh_token.token, None)
        access_token = secrets.token_urlsafe(32)
        new_refresh = secrets.token_urlsafe(32)
        self._access_tokens[access_token] = AccessToken(
            token=access_token,
            client_id=client.client_id,
            scopes=scopes or refresh_token.scopes,
            expires_at=int(time.time()) + 3600 * 24 * 365,
        )
        self._refresh_tokens[new_refresh] = RefreshTokenData(
            token=new_refresh,
            client_id=client.client_id,
            scopes=scopes or refresh_token.scopes,
            expires_at=time.time() + 3600 * 24 * 365,
        )
        return OAuthToken(
            access_token=access_token,
            token_type="Bearer",
            expires_in=3600 * 24 * 365,
            refresh_token=new_refresh,
        )

    async def load_access_token(self, token: str) -> AccessToken | None:
        return self._access_tokens.get(token)

    async def revoke_token(self, token: AuthCode | RefreshTokenData | AccessToken) -> None:
        if isinstance(token, AccessToken):
            self._access_tokens.pop(token.token, None)
        elif isinstance(token, RefreshTokenData):
            self._refresh_tokens.pop(token.token, None)
