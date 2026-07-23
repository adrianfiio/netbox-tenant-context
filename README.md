# NetBox Tenant Context

Seletores **globais de Tenant e Site** para o NetBox. Escolha um tenant e/ou
site uma vez na barra superior e todo o NetBox passa a mostrar apenas os
objetos correspondentes — sem precisar aplicar filtro manual em cada tela.

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

### Cobertura

Filtra automaticamente as listagens e os campos de autocomplete cujo modelo
tem `tenant_id`/`site_id` nativo ou alcançável por relação direta, como:
Devices, Prefixes, IP Addresses, VLANs, Virtual Machines, Clusters, Circuits,
Racks, Contacts, Interfaces, Circuit Terminations, Front/Rear/Console/Power
Ports, entre outros.

Modelos globais/compartilhados (Providers, Circuit Types, etc.) não têm
tenant/site e permanecem visíveis para todos, como esperado.

> ⚠️ Este filtro é de **conveniência de navegação**, não de segurança. Para
> restringir de fato o que um usuário pode ver/editar, use as
> [Object-Based Permissions](https://netboxlabs.com/docs/netbox/administration/permissions/)
> nativas do NetBox com constraints (ex.: `{"tenant_id": 7}`).

---

## Instalação

O plugin é instalado direto deste repositório GitHub, dentro do virtualenv do
próprio NetBox (ajuste o caminho conforme sua instalação, ex.:
`/opt/netbox-4.6.4`).

```bash
# ative o virtualenv do NetBox
source /opt/netbox-4.6.4/venv/bin/activate

# instale a versão mais recente do main
pip install git+https://github.com/adrianfiio/netbox-tenant-context.git

# ou trave numa versão/release específica
pip install git+https://github.com/adrianfiio/netbox-tenant-context.git@v0.2.0
```

Para que a instalação sobreviva a futuras atualizações do NetBox (`upgrade.sh`),
registre também em `local_requirements.txt`:

```bash
echo "git+https://github.com/adrianfiio/netbox-tenant-context.git@v0.2.0" \
  >> /opt/netbox-4.6.4/local_requirements.txt
```

Ative em `netbox/netbox/configuration.py`:

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
cd /opt/netbox-4.6.4
source venv/bin/activate
python netbox/manage.py collectstatic --no-input
sudo systemctl restart netbox netbox-rq
```

> Este plugin não cria tabelas no banco (não há models), então não há
> migrações a rodar.

### Atualizando para uma nova versão

```bash
source /opt/netbox-4.6.4/venv/bin/activate
pip install --force-reinstall git+https://github.com/adrianfiio/netbox-tenant-context.git
sudo systemctl restart netbox netbox-rq
```

---

## Uso

1. No topo do NetBox, abra o seletor de **Tenant** e/ou **Site**.
2. Escolha um valor → as listagens e os campos de formulário passam a
   mostrar/aceitar apenas os objetos correspondentes.
3. Escolha *Todos os Tenants* / *Todos os Sites* para desligar o filtro
   daquela dimensão.

---

## Changelog

Ver [CHANGELOG.md](./CHANGELOG.md).

## Compatibilidade

Ver [COMPATIBILITY.md](./COMPATIBILITY.md).

## Licença

Apache-2.0
