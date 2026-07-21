from netbox.plugins import PluginTemplateExtension
from tenancy.models import Tenant

from netbox_tenant_context.context import get_current_tenant_id


class TenantContextSelector(PluginTemplateExtension):
    """
    Renders the global tenant selector in the top navigation bar.

    NOTE: we deliberately do NOT set a `models` attribute. Per NetBox docs,
    an extension without `models` is invoked on every view -- which is exactly
    what we want for a persistent navbar control.
    """

    def navbar(self):
        request = self.context["request"]
        current_id = get_current_tenant_id(request)

        tenants = Tenant.objects.all().order_by("name")
        current = tenants.filter(pk=current_id).first() if current_id else None

        return self.render(
            "netbox_tenant_context/navbar_selector.html",
            extra_context={
                "tenants": tenants,
                "current": current,
                "current_id": current_id,
            },
        )


template_extensions = [TenantContextSelector]
