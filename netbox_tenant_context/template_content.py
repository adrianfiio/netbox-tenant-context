from netbox.plugins import PluginTemplateExtension
from dcim.models import Site
from tenancy.models import Tenant

from netbox_tenant_context.context import (
    get_current_tenant_id,
    get_current_site_id,
)


class TenantContextSelector(PluginTemplateExtension):
    """
    Renders the global Tenant + Site selectors in the top navigation bar.

    NOTE: no `models` attribute is set. Per NetBox docs, an extension without
    `models` is invoked on every view -- exactly what we want for a
    persistent navbar control.
    """

    def navbar(self):
        request = self.context["request"]

        current_tenant_id = get_current_tenant_id(request)
        tenants = Tenant.objects.all().order_by("name")
        current_tenant = (
            tenants.filter(pk=current_tenant_id).first() if current_tenant_id else None
        )

        current_site_id = get_current_site_id(request)
        sites = Site.objects.all().order_by("name")
        current_site = (
            sites.filter(pk=current_site_id).first() if current_site_id else None
        )

        return self.render(
            "netbox_tenant_context/navbar_selector.html",
            extra_context={
                "tenants": tenants,
                "current_tenant": current_tenant,
                "current_tenant_id": current_tenant_id,
                "sites": sites,
                "current_site": current_site,
                "current_site_id": current_site_id,
            },
        )


template_extensions = [TenantContextSelector]
