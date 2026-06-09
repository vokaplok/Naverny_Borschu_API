from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings


class GoogleAuthError(Exception):
    """Raised when Google token validation fails."""


@dataclass
class GoogleIdentity:
    sub: str
    email: str
    email_verified: bool
    given_name: str
    family_name: str
    full_name: str
    picture: str
    locale: str
    aud: str
    azp: str



def _fetch_json(url: str, *, headers: dict[str, str] | None = None) -> dict[str, Any]:
    request = Request(url, headers=headers or {})
    try:
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except HTTPError as exc:
        body = exc.read().decode('utf-8', errors='ignore')
        raise GoogleAuthError(body or 'Google auth request failed') from exc
    except (TimeoutError, URLError) as exc:
        raise GoogleAuthError('Google auth service is unavailable') from exc



def _configured_google_client_ids() -> set[str]:
    raw = getattr(settings, 'GOOGLE_OAUTH_CLIENT_IDS', None) or []
    return {value.strip() for value in raw if value and value.strip()}



def _validate_audience(aud: str, azp: str) -> None:
    allowed_ids = _configured_google_client_ids()
    if not allowed_ids:
        return

    audience_values = {value for value in (aud, azp) if value}
    if not audience_values.intersection(allowed_ids):
        raise GoogleAuthError('Google token audience is not allowed')



def fetch_google_identity(*, id_token: str | None = None, access_token: str | None = None) -> GoogleIdentity:
    if not id_token and not access_token:
        raise GoogleAuthError('Google token is required')

    token_info: dict[str, Any]
    profile: dict[str, Any]

    if id_token:
        query = urlencode({'id_token': id_token})
        token_info = _fetch_json(f'https://oauth2.googleapis.com/tokeninfo?{query}')
        profile = token_info
    else:
        query = urlencode({'access_token': access_token})
        token_info = _fetch_json(f'https://oauth2.googleapis.com/tokeninfo?{query}')
        profile = _fetch_json(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
        )

    email = (profile.get('email') or '').strip().lower()
    if not email:
        raise GoogleAuthError('Google account did not return an email')
    if not profile.get('email_verified'):
        raise GoogleAuthError('Google email is not verified')

    aud = (token_info.get('aud') or '').strip()
    azp = (token_info.get('azp') or '').strip()
    _validate_audience(aud, azp)

    return GoogleIdentity(
        sub=(profile.get('sub') or token_info.get('sub') or '').strip(),
        email=email,
        email_verified=bool(profile.get('email_verified')),
        given_name=(profile.get('given_name') or '').strip(),
        family_name=(profile.get('family_name') or '').strip(),
        full_name=(profile.get('name') or '').strip(),
        picture=(profile.get('picture') or '').strip(),
        locale=(profile.get('locale') or '').strip(),
        aud=aud,
        azp=azp,
    )
