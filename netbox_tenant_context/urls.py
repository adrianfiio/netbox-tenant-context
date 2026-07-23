from django.urls import path

from netbox_tenant_context.views import SetTenantContextView, SetSiteContextView

app_name = "netbox_tenant_context"

urlpatterns = [
    # /plugins/tenant-context/set/       -> plugins:netbox_tenant_context:set_context
    path("set/", SetTenantContextView.as_view(), name="set_context"),
    # /plugins/tenant-context/set-site/  -> plugins:netbox_tenant_context:set_site_context
    path("set-site/", SetSiteContextView.as_view(), name="set_site_context"),
]
