# TI Ajuda — ETI

Scripts de apoio de TI para o projeto **ETI** (Google Meet + Google Sheets):

1. **Checagem de gravações** dos encontros síncronos no Google Drive, com
   verificação/abertura automática de permissão de compartilhamento.
2. **Monitoramento de status das salas Meet** (ativa/inativa, nº de
   participantes, se está gravando) via Google Meet REST API — usado para
   checar rapidamente se os links de uma sala estão corretos e funcionando.
3. **Modelos de agendamento (cron)** para rodar as checagens automaticamente
   nos horários dos plantões/encontros.

Todos os scripts são **genéricos**: nenhuma credencial, e-mail, ID de
planilha real ou link de Meet fica hardcoded no código — tudo vem de
`config/config.yaml` (copiado a partir de `config/config.example.yaml`) e de
um token OAuth próprio de cada usuário. Isso permite que qualquer colega do
projeto clone o repositório e configure com as próprias credenciais.

## Pré-requisitos

- Python 3.10+
- Uma conta Google de serviço do projeto (ex.: `suporte.xxx@dominio`) com
  OAuth autorizado para os escopos:
  - `https://www.googleapis.com/auth/drive.readonly` (ou `drive` se for
    necessário também ajustar permissões)
  - `https://www.googleapis.com/auth/spreadsheets.readonly`
  - `https://www.googleapis.com/auth/meetings.space.readonly`
- Um **Client ID/Secret OAuth** (Google Cloud Console → APIs & Serviços →
  Credenciais → "OAuth client ID" tipo "Desktop app") com as APIs Drive,
  Sheets e Meet habilitadas no projeto.

## Instalação

```bash
git clone <url-deste-repo>
cd ti-ajuda-eti
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp config/config.example.yaml config/config.yaml
# edite config/config.yaml com seus IDs de planilha, salas e caminhos
```

## Autenticação (gerar o token OAuth local)

```bash
python3 scripts/auth_setup.py
```

Abre um fluxo OAuth no navegador (ou imprime uma URL para copiar/colar em
ambiente sem navegador), pede login com a conta do projeto, e salva o token
em `config/token.json` (caminho configurável). Esse arquivo é sensível —
**nunca commitá-lo** (já está no `.gitignore`).

Veja `docs/oauth_setup.md` para o passo a passo completo de criação do
Client ID no Google Cloud Console.

## Uso

### 1. Checar gravações de um encontro

```bash
python3 scripts/verificar_gravacoes.py --sala BS4 --desde 2026-09-16
```

Lista os arquivos de gravação encontrados no Drive para a sala (filtro por
tag, ex. `BS4`, `CS1`) a partir da data informada, mostra se já estão
compartilhados com "qualquer pessoa com o link" e, se não estiverem, oferece
abrir a permissão (`--abrir-permissao`).

```bash
python3 scripts/verificar_gravacoes.py --sala BS4 --desde 2026-09-16 --abrir-permissao
```

### 2. Checar status/links das salas Meet

```bash
python3 scripts/checar_salas_meet.py --csv config/salas.csv
```

Lê uma lista de salas (nome, link do Meet) de um CSV, verifica que o código
da reunião é válido e consulta a API para reportar: ativa/inativa, nº de
participantes, se está gravando. Útil para confirmar que nenhum link do
plantão está quebrado ou apontando para a sala errada antes do início do
encontro.

Formato esperado do CSV (`config/salas.example.csv`):

```csv
nome,dia_semana,link_meet
Sala 1,segunda,https://meet.google.com/abc-defg-hij
Célula 1 da Sala 1,segunda,https://meet.google.com/klm-nopq-rst
```

### 3. Agendamento (cron)

Modelos prontos de cron (crontab tradicional e agendador Hermes) em
`cron/`, com expressões de exemplo para rodar a checagem de salas X minutos
antes do horário do encontro e enviar o relatório por e-mail/Telegram/
webhook. Veja `cron/README.md`.

## Estrutura

```
ti-ajuda-eti/
├── config/
│   ├── config.example.yaml   # template de configuração (copiar p/ config.yaml)
│   ├── salas.example.csv     # template da lista de salas
│   └── .gitkeep
├── scripts/
│   ├── auth_setup.py          # gera o token OAuth local
│   ├── google_auth.py         # helper de carregamento/refresh de credenciais
│   ├── verificar_gravacoes.py # checa gravações no Drive + permissões
│   └── checar_salas_meet.py   # checa status/links das salas via Meet API
├── cron/
│   ├── README.md
│   └── crontab.example
├── docs/
│   └── oauth_setup.md
├── requirements.txt
└── .gitignore
```

## Segurança

- `config/config.yaml`, `config/token.json`, `config/salas.csv` (com links
  reais) e qualquer `.env` **não são versionados** — estão no
  `.gitignore`. Compartilhe apenas os arquivos `*.example.*`.
- Nunca commitar client secret, token OAuth, e-mails de formadores/cursistas
  ou links reais de Meet/Drive.
