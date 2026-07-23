"""
TenantContextMiddleware

Applies TWO independent, optional filter dimensions -- Tenant and Site --
across NetBox:

1. LIST VIEWS (UI)
   Injects the session-selected tenant_id and/or site_id into NetBox object
   *list* views as query params, so NetBox's own FilterSets do the filtering.

2. AUTOCOMPLETE / API CALLS FROM FORM DROPDOWNS
   Form fields (e.g. "Device" on a circuit termination) search via the REST
   API. Without a filter this returns objects from ALL tenants/sites, so a
   user could accidentally connect a circuit to the wrong tenant's device.
   We inject the correct filter (tenant_id/site_id or the right related
   lookup) into these API calls automatically.

Both dimensions can be active at once (combined with AND), only one, or
neither ("Todos"). Each respects a manual filter the user already applied.
"""

from django.conf import settings

MANUAL_TENANT_PARAMS = ("tenant_id", "tenant", "tenant_group_id", "tenant_group")
MANUAL_SITE_PARAMS = ("site_id", "site", "region_id", "region")

# ---------------------------------------------------------------------------
# TENANT paths
# ---------------------------------------------------------------------------
DIRECT_TENANT_API_PATHS = {
    "/api/dcim/devices/",
    "/api/dcim/racks/",
    "/api/dcim/sites/",
    "/api/dcim/locations/",
    "/api/ipam/prefixes/",
    "/api/ipam/ip-addresses/",
    "/api/ipam/vlans/",
    "/api/ipam/vlan-groups/",
    "/api/ipam/ip-ranges/",
    "/api/circuits/circuits/",
    "/api/virtualization/virtual-machines/",
    "/api/virtualization/clusters/",
    "/api/tenancy/contacts/",
}

RELATED_TENANT_API_PATHS = {
    "/api/dcim/interfaces/": "device__tenant_id",
    "/api/dcim/front-ports/": "device__tenant_id",
    "/api/dcim/rear-ports/": "device__tenant_id",
    "/api/dcim/console-ports/": "device__tenant_id",
    "/api/dcim/console-server-ports/": "device__tenant_id",
    "/api/dcim/power-ports/": "device__tenant_id",
    "/api/dcim/power-outlets/": "device__tenant_id",
    "/api/circuits/circuit-terminations/": "circuit__tenant_id",
    "/api/virtualization/interfaces/": "virtual_machine__tenant_id",
}

# ---------------------------------------------------------------------------
# SITE paths
# ---------------------------------------------------------------------------
DIRECT_SITE_API_PATHS = {
    "/api/dcim/devices/",
    "/api/dcim/racks/",
    "/api/dcim/locations/",
    "/api/dcim/power-panels/",
    "/api/dcim/power-feeds/",
    "/api/ipam/vlans/",
    "/api/ipam/prefixes/",
    "/api/circuits/circuit-terminations/",
}

RELATED_SITE_API_PATHS = {
    "/api/dcim/interfaces/": "device__site_id",
    "/api/dcim/front-ports/": "device__site_id",
    "/api/dcim/rear-ports/": "device__site_id",
    "/api/dcim/console-ports/": "device__site_id",
    "/api/dcim/console-server-ports/": "device__site_id",
    "/api/dcim/power-ports/": "device__site_id",
    "/api/dcim/power-outlets/": "device__site_id",
    "/api/virtualization/interfaces/": "virtual_machine__site_id",
}


class TenantContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self._maybe_inject_api_filters(request)
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Inject tenant_id / site_id into UI list views."""
        view_class = getattr(view_func, "view_class", None)
        if view_class is None:
            return None

        try:
            from netbox.views.generic import ObjectListView
        except Exception:
            return None

        if not issubclass(view_class, ObjectListView):
            return None

        from netbox_tenant_context.context import (
            get_current_tenant_id,
            get_current_site_id,
            user_bypasses_filter,
        )

        if user_bypasses_filter(request):
            return None

        respect_manual = (
            settings.PLUGINS_CONFIG.get("netbox_tenant_context", {})
            .get("respect_manual_filter", True)
        )

        params = request.GET.copy()
        changed = False

        tenant_id = get_current_tenant_id(request)
        if tenant_id and not (respect_manual and any(p in request.GET for p in MANUAL_TENANT_PARAMS)):
            params["tenant_id"] = str(tenant_id)
            changed = True

        site_id = get_current_site_id(request)
        if site_id and not (respect_manual and any(p in request.GET for p in MANUAL_SITE_PARAMS)):
            params["site_id"] = str(site_id)
            changed = True

        if changed:
            request.GET = params
        return None

    # ------------------------------------------------------------------
    # API autocomplete injection
    # ------------------------------------------------------------------

    def _maybe_inject_api_filters(self, request):
        if request.method != "GET":
            return

        path = request.path_info

        tenant_param = None
        if path in DIRECT_TENANT_API_PATHS:
            tenant_param = "tenant_id"
        elif path in RELATED_TENANT_API_PATHS:
            tenant_param = RELATED_TENANT_API_PATHS[path]

        site_param = None
        if path in DIRECT_SITE_API_PATHS:
            site_param = "site_id"
        elif path in RELATED_SITE_API_PATHS:
            site_param = RELATED_SITE_API_PATHS[path]

        if tenant_param is None and site_param is None:
            return

        from netbox_tenant_context.context import (
            get_current_tenant_id,
            get_current_site_id,
            user_bypasses_filter,
        )

        if user_bypasses_filter(request):
            return

        params = request.GET.copy()
        changed = False

        if tenant_param and not any(p in request.GET for p in MANUAL_TENANT_PARAMS):
            tenant_id = get_current_tenant_id(request)
            if tenant_id:
                params[tenant_param] = str(tenant_id)
                changed = True

        if site_param and not any(p in request.GET for p in MANUAL_SITE_PARAMS):
            site_id = get_current_site_id(request)
            if site_id:
                params[site_param] = str(site_id)
                changed = True

        if changed:
            request.GET = params
