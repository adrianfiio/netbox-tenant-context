# NetBox Tenant Context

Seletor **global de Tenant** para o NetBox. Escolha um tenant uma vez na barra
superior e todo o NetBox passa a mostrar apenas os objetos daquele tenant — sem
precisar aplicar filtro manual em cada tela.

Compatível com **NetBox 4.6.x** (Django 6.0 / Python 3.12+).

---

## Como funciona

- Dois **seletores independentes** aparecem na barra de navegação: **Tenant**
  e **Site**. Cada um pode ficar em "Todos" ou apontar para um valor
  específico — e os dois podem estar ativos ao mesmo tempo (combinados com
  AND).
- A escolha é gravada **na sessão do usuário** (cada usuário tem seu próprio
  contexto).
- Um **middleware** injeta `tenant_id` / `site_id` tanto nas *list views*
  quanto nas chamadas de API usadas pelos campos de busca/autocomplete dos
  formulários (ex.: escolher um Device numa terminação de circuito), evitando
  conectar objetos de tenants ou sites diferentes por engano.

### Cobertura (V1)

Filtra automaticamente as listagens cujo modelo tem filtro `tenant_id` nativo,
como: Devices, Prefixes, IP Addresses, VLANs, Virtual Machines, Clusters,
Circuits, Racks, Contacts, entre outros.

Ainda **não** cobre modelos sem `tenant_id` no FilterSet (ex.: Interfaces,
Cables), que dependem de resolver o tenant por um objeto relacionado. Isso está
planejado para a V2.

---

## Instalação (bare-metal, `/opt/netbox`)

```bash
# entre no virtualenv do NetBox
source /opt/netbox/venv/bin/activate

# instale o plugin (ajuste o caminho)
pip install /caminho/para/netbox-tenant-context
# ou, para desenvolvimento:
pip install -e /caminho/para/netbox-tenant-context
```

Ative em `/opt/netbox/netbox/netbox/configuration.py`:

```python
PLUGINS = [
    "netbox_tenant_context",
]

# opcional
PLUGINS_CONFIG = {
    "netbox_tenant_context": {
        "respect_manual_filter": True,   # não sobrescreve filtro manual do usuário
        "bypass_groups": [],             # grupos que ignoram o filtro automático
    },
}
```

Aplique e reinicie:

```bash
cd /opt/netbox
source venv/bin/activate
python netbox/manage.py collectstatic --no-input
sudo systemctl restart netbox netbox-rq
```

> Este plugin não cria tabelas no banco (não há models), então não há migrações
> a rodar.

---

## Uso

1. No topo do NetBox, abra o seletor de contexto.
2. Escolha um tenant → as listagens passam a mostrar só os objetos dele.
3. Escolha *Todos os Tenants* para desligar o filtro.

---

## Licença

Apache-2.0
