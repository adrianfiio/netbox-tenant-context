"""
TenantContextMiddleware

Injects the session-selected tenant into NetBox object *list* views as a
`tenant_id` query parameter, so NetBox's own FilterSets do the filtering.

Why this approach (vs. patching querysets or model managers):
  - It reuses NetBox's native, per-model tenant filters -> low maintenance.
  - It never touches detail/edit/delete/API paths -> fewer surprises.
  - It survives NetBox upgrades better, because it depends only on the
    public ObjectListView base class and the public `tenant_id` filter.

Known limitation (planned for V2): models whose FilterSet has no `tenant_id`
filter (e.g. Interface, Cable) simply ignore the injected param, so those
lists are not filtered yet. Those need tenant resolution via a related object.
"""

from django.conf import settings

# Query params that mean "the user already chose a tenant scope themselves".
# When any of these is present we leave the request untouched.
MANUAL_FILTER_PARAMS = ("tenant_id", "tenant", "tenant_group_id", "tenant_group")


class TenantContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Class-based views expose the class via `.view_class`.
        view_class = getattr(view_func, "view_class", None)
        if view_class is None:
            return None

        # Import lazily to avoid AppRegistryNotReady during startup.
        try:
            from netbox.views.generic import ObjectListView
        except Exception:
            return None

        # Only act on list views. Detail/edit/bulk views are left alone.
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
            # "Todos os Tenants" -> no filtering.
            return None

        respect_manual = (
            settings.PLUGINS_CONFIG.get("netbox_tenant_context", {})
            .get("respect_manual_filter", True)
        )
        if respect_manual and any(p in request.GET for p in MANUAL_FILTER_PARAMS):
            return None

        # Inject tenant_id so the view's FilterSet picks it up.
        params = request.GET.copy()
        params["tenant_id"] = str(tenant_id)
        request.GET = params
        return None
