"""
Helpers to read/write the active tenant stored in the user's session.

Everything here is intentionally tiny and dependency-free so it can be imported
from the middleware, the views, and the template extension without circular
import problems.
"""

from django.conf import settings

PLUGIN_NAME = "netbox_tenant_context"


def _cfg(key, default=None):
    return settings.PLUGINS_CONFIG.get(PLUGIN_NAME, {}).get(key, default)


def get_session_key():
    return _cfg("session_key", "tenant_context_id")


def get_current_tenant_id(request):
    """
    Return the tenant id stored in the user's session, or None when the
    context is "Todos os Tenants" (no filter).
    """
    session = getattr(request, "session", None)
    if session is None:
        return None
    value = session.get(get_session_key())
    try:
        return int(value) if value else None
    except (TypeError, ValueError):
        return None


def set_current_tenant_id(request, tenant_id):
    """Persist the chosen tenant (or clear it when tenant_id is falsy)."""
    key = get_session_key()
    if tenant_id:
        request.session[key] = int(tenant_id)
    else:
        request.session.pop(key, None)


def user_bypasses_filter(request):
    """
    True when the automatic filter should NOT be applied for this user
    (e.g. members of a configured bypass group).
    """
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        # Anonymous requests have no session tenant anyway.
        return True

    groups = _cfg("bypass_groups", []) or []
    if groups and user.groups.filter(name__in=groups).exists():
        return True

    return False
