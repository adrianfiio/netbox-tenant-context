from netbox.plugins import PluginConfig
from .version import __version__


class TenantContextConfig(PluginConfig):
    name = "netbox_tenant_context"
    verbose_name = "NetBox Tenant Context"
    description = (
        "Global tenant and site context switcher: pick a tenant and/or "
        "site once and the whole NetBox UI is automatically filtered to it."
    )
    version = __version__
    author = "Adrian Fiio"
    author_email = "adrian_tbr@hotmail.com"
    base_url = "tenant-context"

    # Compatível com a linha 4.6.x (Django 6.0 / Python 3.12+).
    min_version = "4.6.0"
    max_version = "4.6.99"

    # Middleware que injeta o tenant/site da sessão nas list views e nas
    # chamadas de API usadas pelos campos de autocomplete dos formulários.
    # É anexado DEPOIS do middleware nativo do NetBox (sessão/auth já resolvidos).
    middleware = ["netbox_tenant_context.middleware.TenantContextMiddleware"]

    default_settings = {
        # Chave usada na sessão do usuário para guardar o tenant ativo.
        "session_key": "tenant_context_id",
        # Chave usada na sessão do usuário para guardar o site ativo.
        "site_session_key": "site_context_id",
        # Se o usuário aplicar um filtro manual de tenant/site na tela,
        # respeitamos e NÃO sobrescrevemos.
        "respect_manual_filter": True,
        # Usuários nesses grupos ignoram o filtro automático por completo.
        # (os botões "Todos os Tenants" / "Todos os Sites" já permitem
        # desligar caso a caso)
        "bypass_groups": [],
    }
    required_settings = []


config = TenantContextConfig
