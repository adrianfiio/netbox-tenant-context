from django.urls import path

from netbox_tenant_context.views import SetTenantContextView

app_name = "netbox_tenant_context"

urlpatterns = [
    # Final URL: /plugins/tenant-context/set/
    # Reverse name: plugins:netbox_tenant_context:set_context
    path("set/", SetTenantContextView.as_view(), name="set_context"),
]
