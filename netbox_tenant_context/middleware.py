"""
TenantContextMiddleware

Two jobs:

1. LIST VIEWS (UI)
   Injects the session-selected tenant into NetBox object *list* views as a
   `tenant_id` query parameter, so NetBox's own FilterSets do the filtering.

2. AUTOCOMPLETE / API CALLS FROM FORM DROPDOWNS
   When a form field (e.g. "Device" on a circuit termination) opens a search
   dropdown it calls the REST API, e.g.:
       GET /api/dcim/devices/?q=router&brief=1
   Without a tenant filter this returns devices from ALL tenants, causing the
   user to accidentally connect a circuit to the wrong tenant's device.

   We intercept these API calls and inject tenant_id (or the correct lookup
   path for models that don't have a direct tenant field) automatically.
"""

from django.conf import settings

MANUAL_FILTER_PARAMS = ("tenant_id", "tenant", "tenant_group_id", "tenant_group")

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


class TenantContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self._maybe_inject_api_tenant(request)
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
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
            user_bypasses_filter,
        )

        if user_bypasses_filter(request):
            return None

        tenant_id = get_current_tenant_id(request)
        if not tenant_id:
            return None

        respect_manual = (
            settings.PLUGINS_CONFIG.get("netbox_tenant_context", {})
            .get("respect_manual_filter", True)
        )
        if respect_manual and any(p in request.GET for p in MANUAL_FILTER_PARAMS):
            return None

        params = request.GET.copy()
        params["tenant_id"] = str(tenant_id)
        request.GET = params
        return None

    def _maybe_inject_api_tenant(self, request):
        if request.method != "GET":
            return

        path = request.path_info

        filter_param = None
        if path in DIRECT_TENANT_API_PATHS:
            filter_param = "tenant_id"
        elif path in RELATED_TENANT_API_PATHS:
            filter_param = RELATED_TENANT_API_PATHS[path]

        if filter_param is None:
            return

        if any(p in request.GET for p in MANUAL_FILTER_PARAMS):
            return

        from netbox_tenant_context.context import (
            get_current_tenant_id,
            user_bypasses_filter,
        )

        if user_bypasses_filter(request):
            return

        tenant_id = get_current_tenant_id(request)
        if not tenant_id:
            return

        params = request.GET.copy()
        params[filter_param] = str(tenant_id)
        request.GET = params
