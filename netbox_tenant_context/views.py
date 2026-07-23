from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from dcim.models import Site
from tenancy.models import Tenant

from netbox_tenant_context.context import (
    set_current_tenant_id,
    set_current_site_id,
)


class _BaseContextView(View):
    """Shared redirect-back logic for the two context-setter views."""

    def get(self, request):
        return redirect(reverse("home"))

    def _back(self, request):
        nxt = (
            request.POST.get("next")
            or request.META.get("HTTP_REFERER")
            or reverse("home")
        )
        if url_has_allowed_host_and_scheme(
            nxt,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(nxt)
        return redirect(reverse("home"))


class SetTenantContextView(_BaseContextView):
    """Stores the chosen Tenant in the user's session."""

    def post(self, request):
        raw = (request.POST.get("tenant") or "").strip()

        if raw in ("", "all", "0"):
            set_current_tenant_id(request, None)
            messages.info(request, "Contexto de Tenant: Todos os Tenants.")
            return self._back(request)

        try:
            tenant = Tenant.objects.get(pk=int(raw))
        except (Tenant.DoesNotExist, ValueError):
            messages.error(request, "Tenant inválido.")
            return self._back(request)

        set_current_tenant_id(request, tenant.pk)
        messages.success(request, f"Contexto de Tenant ativo: {tenant.name}.")
        return self._back(request)


class SetSiteContextView(_BaseContextView):
    """Stores the chosen Site in the user's session."""

    def post(self, request):
        raw = (request.POST.get("site") or "").strip()

        if raw in ("", "all", "0"):
            set_current_site_id(request, None)
            messages.info(request, "Contexto de Site: Todos os Sites.")
            return self._back(request)

        try:
            site = Site.objects.get(pk=int(raw))
        except (Site.DoesNotExist, ValueError):
            messages.error(request, "Site inválido.")
            return self._back(request)

        set_current_site_id(request, site.pk)
        messages.success(request, f"Contexto de Site ativo: {site.name}.")
        return self._back(request)
