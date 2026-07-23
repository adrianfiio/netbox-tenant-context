# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

## [0.2.0] - 2026-07-23

### Adicionado
- Seletor global de **Site**, independente do Tenant, na barra de navegação.
- Tenant e Site agora podem ser combinados (AND) para refinar o contexto
  (ex.: Tenant "Duoward" + Site "Curitiba").
- Filtro automático de Site nas *list views* do NetBox.
- Filtro automático de Site nos endpoints de API usados pelos campos de
  autocomplete de formulário (Device, Interface, Circuit Termination, etc.),
  evitando conexões de circuito/rede entre devices de sites diferentes.
- Nova configuração `site_session_key` em `PLUGINS_CONFIG`.

### Alterado
- `SetTenantContextView` foi reorganizada; nova `SetSiteContextView` para
  gravar o site ativo na sessão.
- Novo endpoint: `/plugins/tenant-context/set-site/`.

## [0.1.0] - 2026-07-23

### Adicionado
- Seletor global de **Tenant** na barra de navegação do NetBox.
- Middleware que injeta `tenant_id` automaticamente nas listagens.
- Contexto salvo por sessão de usuário, com opção "Todos os Tenants".
- Compatível com NetBox 4.6.x.
