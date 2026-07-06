# EIT App — Gerenciamento de Projetos de Engenharia de Transporte

> 🇧🇷 Português · 🇪🇸 [Español](README.md) · 🇺🇸 [English](README.en.md)

Backend Django para gerenciamento de projetos de engenharia de transporte, modelagem de redes viárias, contagens veiculares, análise de fluxos e exportação para TRANSYT 8S.

## Funcionalidades

- **Mandantes e Contatos**: Gerenciamento de clientes/organizações com contatos associados. Interface em espanhol.
- **Projetos**: Criação, acompanhamento, imagens (drag-drop / colar / seletor de arquivos), status (ativo / finalizado).
- **Rede Viária**: Modelagem completa de rede — ruas, nós (interseções), arcos (segmentos), regulamentações (PARE/DÊ_PREFERÊNCIA/SEMÁFORO/LIVRE), pontos de controle (movimentos por interseção).
- **Periodização**: Contagens veiculares manuais em intervalos de 15 minutos por ponto de controle e período. 8 tipos veiculares (VL, TXC, TXB, C2E, C_mas2E, pedestre, ciclista, moto) com cálculo automático de fluxo total (ftot) usando fatores de equivalência.
- **Coeficientes de Cruzamento**: Fatores de equivalência veicular em dois níveis — padrões globais + sobrescrita por projeto. Resolução por herança.
- **Análise de Fluxos**: Dashboard com tabela de dados, ranking de pontos de controle por fluxo, tabela comparativa (PCs vs períodos) e gráfico Chart.js de barras agrupadas. Recálculo agregado a partir da periodização.
- **TRANSYT 8S**: Configuração global (ciclo, W, K), parâmetros de arco (fluxo de saturação, ponderadores), fases semafóricas (verde início/fim). Geração de arquivo .dat no formato TRANSYT-8S (largura fixa de 80 colunas) com cards header/1/2/11/31/32. Exportação por período individual (.dat) ou múltiplo (.zip).
- **Autenticação**: Registro, login, logout. Proteção `@login_required` em todas as views.
- **UI**: Design consistente com Tailwind CSS, modais, tabelas editáveis inline com HTMX, formulários com labels em espanhol, campos editáveis com contraste melhorado.

## Stack Tecnológica

- **Python 3.11** + **Django 5.2**
- **PostgreSQL** (multi-DB: default + ORA para VPS)
- HTMX 2.x para interatividade (CRUD inline)
- Tailwind CSS v4 (modo dev com `python manage.py tailwind.dev`)
- WhiteNoise para arquivos estáticos
- Chart.js 4.x para gráficos de análise
- Font Awesome 6 (CDN) para iconografia
- Sistema de arquivos local para imagens (sem Supabase)

## Ferramentas

| Ferramenta | Uso |
|------------|-----|
| **ruff** | Linter + formatador Python |
| **ESLint** | Linter JavaScript |
| **Prettier** | Formatador JavaScript |
| **pre-commit** | Hooks automáticos do Git |
| **coverage** | Cobertura de testes (mín. 80%) |
| **pytest** | Runner de testes |

## Estrutura de Apps

| App | Descrição | Status |
|-----|-----------|--------|
| mandantes | Clientes (mandantes) e contatos | ✅ |
| proyectos | Projetos de tráfego com imagens e status | ✅ |
| red_vial | Rede viária, periodização, análise, TRANSYT | ✅ |
| usuarios | Autenticação e perfis | ✅ |
| tasks | Demonstração / testes (a ser removido em breve) | ⚠️ |

## Fluxo de Trabalho (Mini Manual)

```
1. MANDANTE → /mandantes/
   Criar cliente/organização.
   Criar cliente/organização.
   Adicionar contatos associados (nome, email, telefone, cargo).

2. PROJETO → /proyectos/ → "Criar Projeto"
   Associar a um mandante. Preencher dados gerais, enviar imagem.
   O projeto pode estar Ativo ou Finalizado.

3. REDE VIÁRIA → /proyectos/<id>/resumen/
   Resumo do projeto com quantidades de ruas, nós, arcos, PCs.
   Acesso a cada seção de modelagem:

   a. Ruas → Definir ruas da área de estudo
   b. Nós → Definir interseções (cruzamento de 2 ruas)
   c. Arcos → Conectar nós (origem → destino) com comprimento
   d. Regulamentações → PARE / DÊ_PREFERÊNCIA / SEMÁFORO / LIVRE
   e. Pontos de Controle → Atribuir movimento (6 direções),
      conversão (DIR/DER/ESQ), arco entrada/saída, regulamentação, pistas
   f. Períodos → Definir janelas de análise (AM-P, PM-P, etc.)
   g. Coeficientes de Cruzamento → Fatores de equivalência veicular
      (padrão global + sobrescrita por projeto)

4. PERIODIZAÇÃO → /proyectos/<id>/periodizacion/
   Selecionar nós (PCs), períodos, movimento, data.
   "Gerar" → cria linhas de intervalos de 15 min.
   Inserir contagens por tipo veicular (VL, TXC, TXB, etc.).
   ftot é calculado automaticamente.

5. ANÁLISE DE FLUXOS → /proyectos/<id>/analisis-flujos/
   Filtrar por nó, período, movimento, data.
   Visualizar:
   - Tabela detalhe (fluxo total, média, registros)
   - Ranking (PCs ordenados por fluxo descendente)
   - Comparativa (PCs vs períodos, tabela pivô)
   - Gráfico Chart.js (barras agrupadas por PC e período)
   "Recalcular" para agregar dados de periodização ao ResumenFlujo.

6. TRANSYT → /proyectos/<id>/configuracion-transyt/
   a. Configuração global → ciclo, W, K, perda/ganho
   b. Parâmetros de Arco → fluxo de saturação, ponderadores
      (1 por PC, com geração automática de defaults)
   c. Fases Semafóricas → verde início/fim por PC e fase
      (com geração automática de fase 1 por PC)

7. EXPORTAR .dat → A partir do detalhe do projeto
   Validar dados completos. Selecionar período ou "todos".
   Gera arquivo TRANSYT-8S (.dat por período, .zip para todos).
   Formato largura fixa de 80 colunas com validação de saída.
```

## URLs Principais

| Rota | View |
|------|------|
| `/` | Dashboard / Home |
| `/signin/` | Login |
| `/usuarios/` | Gerenciamento de usuários (admin) |
| `/mandantes/` | Lista de mandantes |
| `/mandantes/create/` | Criar mandante |
| `/mandantes/<id>/` | Detalhe / editar mandante |
| `/proyectos/` | Lista de projetos |
| `/proyectos/<id>/` | Detalhe do projeto |
| `/proyectos/<id>/resumen/` | Resumo da rede viária |
| `/proyectos/<id>/generar-dat/` | Exportar TRANSYT .dat |
| `/red-vial/proyecto/<id>/calles/` | Gerenciamento de ruas |
| `/red-vial/proyecto/<id>/nodos/` | Gerenciamento de nós |
| `/red-vial/proyecto/<id>/arcos/` | Gerenciamento de arcos |
| `/red-vial/proyecto/<id>/puntos-control/` | Pontos de controle |
| `/red-vial/proyecto/<id>/periodizacion/` | Contagens veiculares |
| `/red-vial/proyecto/<id>/analisis-flujos/` | Dashboard de fluxos |
| `/red-vial/proyecto/<id>/configuracion-transyt/` | Configuração TRANSYT |
| `/red-vial/proyecto/<id>/parametros-arco/` | Parâmetros de arco |
| `/red-vial/proyecto/<id>/fases-semaforicas/` | Fases semafóricas |

## Branches

| Branch | Propósito | Protegida | CI |
|--------|-----------|-----------|----|
| `main` | Produção | Sim (PR + checks) | Apenas manual (workflow_dispatch) |
| `staging` | Pré-produção | Sim (PR + checks) | Auto-deploy ao push |
| `feature/*` | Desenvolvimento | Não | lint + test no PR |
| `fix/*` | Hotfix | Não | lint + test no PR |

## Ambientes

| Ambiente | DB | URL | Deploy |
|----------|----|-----|--------|
| local | PostgreSQL local (eitapp) | localhost:8000 | `python manage.py runserver` |
| staging | PostgreSQL (VPS ORA) | — | Automático ao merge no `staging` |
| production | PostgreSQL (VPS ORA) | — | Manual via GitHub Actions |

### Arquitetura Multi-DB

```
                    ┌──────────────────────────────┐
                    │      Django (settings.py)      │
                    │  default: DATABASE_URL cascade   │
                    │  ORA: DATABASE_URL_ORA (VPS)    │
                    │  pg_local: DATABASE_URL_LOCAL   │
                    └──────┬───────────────┬─────────┘
                           │               │
              ┌────────────┘               └────────────┐
              ▼                                          ▼
   ┌──────────────────┐                    ┌──────────────────────┐
   │  localhost:5432   │                    │  161.153.14.37:5432  │
   │  eitapp (default) │                    │  eitapp (ORA)       │
   │  PG nativo        │                    │  Coolify / Docker   │
   └──────────────────┘                    └──────────────────────┘
```

### Resolução de `default`

```
DATABASE_URL=postgresql://user:pass@host:5432/eitapp    ← se definido
  ↓ não
DATABASE_URL_ORA=postgresql://user:pass@161.153.14.37:5432/eitapp    ← VPS
  ↓ não
postgresql://postgres:1234@localhost:5432/eitapp    ← fallback local
```

- **Local**: `DATABASE_URL` aponta para PostgreSQL local (`eitapp`). `ORA` disponível para alternar.
- **VPS (Coolify)**: Apenas `DATABASE_URL_ORA` está definido → `default` cai em ORA automaticamente. Sem configuração extra.

### Multi-tenancy (futuro)

A aplicação suportará dois modelos de implantação:

```
┌───────────────────────────────────────────────────────────────┐
│                   Balanceador / Proxy                          │
│                 (nginx + server_name ou path)                   │
└──────┬─────────────────────────┬───────────────────────────────┘
       │                         │
       ▼                         ▼
┌──────────────────┐   ┌───────────────────────────┐
│  Plano Compartido │   │    Plano Pro (consultora) │
│  DB compartilhada │   │  Stack Docker individual:  │
│  schema: tenant_* │   │  - web (Django)            │
│  (postgres1)      │   │  - db (PostgreSQL)         │
│                   │   │  - pgadmin4 (opcional)    │
│  Único pgAdmin    │   │  - redis (futuro)         │
│  multi-schema     │   │                            │
└──────────────────┘   └───────────────────────────┘
```

| Fator | Compartido | Pro |
|-------|-----------|------|
| Isolamento de dados | Schema | Database independente |
| Custo | Baixo (1 VPS) | Médio (1 VPS por tenant) |
| Escala | Até ~50 tenants | Ilimitado |
| Backup | Completo + schema dump | Completo por stack |
| Upgrade | Um deploy | Por stack (rollback individual) |
| Provisionamento | `CREATE SCHEMA` | `docker compose up` |

**Status:** Design definido. Pendente de implementação (`ActiveDatabaseRouter` + `TenantMiddleware`).

## CI/CD

Os pipelines do GitHub Actions são executados em cada PR/push para `staging`:

1. **Lint** — ruff (Python) + ESLint + Prettier (JS)
2. **Test** — pytest + coverage (limiar 80%)
3. **Build** — collectstatic
4. **Deploy Staging** — automático ao push para `staging`
5. **Deploy Production** — manual via `workflow_dispatch`

## Início Rápido

```bash
# Clonar e criar ambiente virtual
python -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pre-commit install

# Configurar ambiente
cp .env.example .env

# Migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Executar
python manage.py runserver

# Modo desenvolvimento (Tailwind):
python manage.py tailwind.dev
```

### Lint & Format (local)

```bash
ruff check .                          # Lint Python
ruff format --check .                 # Verificação de formatação Python
npm run lint                          # Lint JS
npm run format                        # Verificação de formatação JS
pre-commit run --all-files            # Tudo junto
```

## Variáveis de Ambiente

```
SECRET_KEY=...
DEBUG=True
DATABASE_URL=...
```

## Licença

MIT
