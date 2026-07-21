from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from tenancy.models import Tenant

from netbox_tenant_context.context import set_current_tenant_id


class SetTenantContextView(View):
    """
    Receives the tenant selection from the navbar dropdown, stores it in the
    user's session, and bounces the user back to the page they were on.
    """

    def post(self, request):
        raw = (request.POST.get("tenant") or "").strip()

        # "all" / empty / "0" => clear the context (Todos os Tenants).
        if raw in ("", "all", "0"):
            set_current_tenant_id(request, None)
            messages.info(request, "Contexto: Todos os Tenants.")
            return self._back(request)

        try:
            tenant = Tenant.objects.get(pk=int(raw))
        except (Tenant.DoesNotExist, ValueError):
            messages.error(request, "Tenant inválido.")
            return self._back(request)

        set_current_tenant_id(request, tenant.pk)
        messages.success(request, f"Contexto ativo: {tenant.name}.")
        return self._back(request)

    def get(self, request):
        # Not meant to be opened directly; send the user home.
        return redirect(reverse("home"))

    def _back(self, request):
        nxt = (
            request.POST.get("next")
            or request.META.get("HTTP_REFERER")
            or reverse("home")
        )
        # Guard against open-redirects.
        if url_has_allowed_host_and_scheme(
            nxt,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(nxt)
        return redirect(reverse("home"))
