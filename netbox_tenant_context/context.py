"""
Helpers to read/write the active context (Tenant and/or Site) stored in the
user's session.

Everything here is intentionally tiny and dependency-free so it can be imported
from the middleware, the views, and the template extension without circular
import problems.

Tenant and Site are independent, optional dimensions. Both can be active at
once (AND'd together), only one, or neither ("Todos").
"""

from django.conf import settings

PLUGIN_NAME = "netbox_tenant_context"


def _cfg(key, default=None):
    return settings.PLUGINS_CONFIG.get(PLUGIN_NAME, {}).get(key, default)


def _get_id(request, session_key):
    session = getattr(request, "session", None)
    if session is None:
        return None
    value = session.get(session_key)
    try:
        return int(value) if value else None
    except (TypeError, ValueError):
        return None


def _set_id(request, session_key, value):
    if value:
        request.session[session_key] = int(value)
    else:
        request.session.pop(session_key, None)


# ---------------------------------------------------------------------------
# Tenant
# ---------------------------------------------------------------------------

def get_session_key():
    return _cfg("session_key", "tenant_context_id")


def get_current_tenant_id(request):
    return _get_id(request, get_session_key())


def set_current_tenant_id(request, tenant_id):
    _set_id(request, get_session_key(), tenant_id)


# ---------------------------------------------------------------------------
# Site
# ---------------------------------------------------------------------------

def get_site_session_key():
    return _cfg("site_session_key", "site_context_id")


def get_current_site_id(request):
    return _get_id(request, get_site_session_key())


def set_current_site_id(request, site_id):
    _set_id(request, get_site_session_key(), site_id)


# ---------------------------------------------------------------------------
# Bypass
# ---------------------------------------------------------------------------

def user_bypasses_filter(request):
    """
    True when the automatic filter should NOT be applied for this user
    (e.g. members of a configured bypass group).
    """
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return True

    groups = _cfg("bypass_groups", []) or []
    if groups and user.groups.filter(name__in=groups).exists():
        return True

    return False
