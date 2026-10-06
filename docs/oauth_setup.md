# Criando um OAuth Client ID no Google Cloud Console

Passos para gerar o `client_secret.json` usado por `scripts/auth_setup.py`.

1. Acesse https://console.cloud.google.com/ com a conta Google que será
   usada pelos scripts (ex.: uma conta de serviço/suporte do projeto, não
   necessariamente sua conta pessoal).
2. Crie um projeto novo (ou use um existente) em "Selecionar projeto" no
   topo da página.
3. Vá em **APIs e Serviços → Biblioteca** e habilite:
   - **Google Drive API**
   - **Google Sheets API**
   - **Google Meet API**
4. Vá em **APIs e Serviços → Tela de consentimento OAuth**:
   - Tipo: "Externo" (ou "Interno" se for conta Google Workspace do
     domínio do projeto).
   - Preencha nome do app, e-mail de suporte, e-mail de contato.
   - Em "Escopos", não é necessário adicionar nada aqui (os scripts pedem
     em tempo de execução).
   - Em "Usuários de teste" (se o app ficar em modo de teste), adicione o
     e-mail da conta que vai autenticar.
5. Vá em **APIs e Serviços → Credenciais → Criar credenciais → ID do
   cliente OAuth**:
   - Tipo de aplicativo: **"App para computador" (Desktop app)**.
   - Dê um nome (ex.: "TI Ajuda ETI - Desktop").
   - Clique em "Criar" e depois em "Fazer download do JSON".
6. Salve o JSON baixado como `config/client_secret.json` (ou outro caminho,
   ajustando `google.client_secret_path` em `config/config.yaml`).
7. Rode `python3 scripts/auth_setup.py` e faça login com a conta do
   projeto quando o navegador abrir.

## Ambiente sem navegador (servidor remoto / SSH)

Se `flow.run_local_server()` não conseguir abrir um navegador local, edite
`scripts/auth_setup.py` trocando a chamada por `flow.run_console()` — o
fluxo imprime uma URL no terminal; abra-a em qualquer navegador (inclusive
na sua máquina local), autorize, copie o código exibido e cole de volta no
terminal onde o script está rodando.

## Escopos usados

| Escopo | Para que serve |
|---|---|
| `drive.readonly` | Listar/ler gravações no Drive (`verificar_gravacoes.py`) |
| `spreadsheets.readonly` | Ler planilhas de turmas/salas, se usado como fonte dos links |
| `meetings.space.readonly` | Consultar status das salas Meet (`checar_salas_meet.py`) |

Se também quiser que o script **abra** permissões de compartilhamento
(`--abrir-permissao` em `verificar_gravacoes.py`), o escopo
`drive.readonly` não é suficiente — troque por `drive` (leitura e escrita)
em `config/config.yaml` e reautorize com `scripts/auth_setup.py`.
