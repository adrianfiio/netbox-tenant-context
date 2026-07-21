# NetBox Tenant Context

Seletor **global de Tenant** para o NetBox. Escolha um tenant uma vez na barra
superior e todo o NetBox passa a mostrar apenas os objetos daquele tenant — sem
precisar aplicar filtro manual em cada tela.

Compatível com **NetBox 4.6.x** (Django 6.0 / Python 3.12+).

---

## Como funciona

- Um **seletor** aparece na barra de navegação (via `navbar()`), com a opção
  *Todos os Tenants* e a lista de tenants cadastrados.
- A escolha é gravada **na sessão do usuário** (cada usuário tem seu contexto).
- Um **middleware** injeta `tenant_id=<escolhido>` nas *list views* do NetBox,
  reaproveitando os FilterSets nativos. Ou seja: nada de reescrever querysets ou
  managers, o que mantém o plugin estável entre versões.

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

## Roadmap

- **V2:** Interfaces, Cables e demais objetos via tenant do objeto relacionado;
  filtro opcional na API REST; busca no seletor.
- **V3:** restringir usuários a um único tenant; tenant padrão por usuário;
  auditoria.

## Licença

Apache-2.0
