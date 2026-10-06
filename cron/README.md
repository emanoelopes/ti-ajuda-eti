# Agendamento das checagens

Dois exemplos de agendamento equivalentes: crontab tradicional do Linux, e
Hermes `cronjob_manage` (se você usa o Hermes como orquestrador).

## Opção 1 — crontab tradicional

Veja `crontab.example`. Copie as linhas relevantes com `crontab -e`,
ajustando caminhos (`cd` para a pasta do repo, ativar o venv) e os horários
para o cronograma real dos seus encontros.

Ideia geral: rodar `checar_salas_meet.py` ~10-15 min antes do início de cada
encontro, registrando a saída em log ou enviando por algum canal
(e-mail/webhook/Telegram — não incluso aqui, adicione conforme sua
infraestrutura). Rodar `verificar_gravacoes.py` algumas horas depois do
término, para confirmar que a gravação já subiu ao Drive.

## Opção 2 — Hermes cronjob

Se for usar o Hermes como orquestrador em vez de crontab puro:

```python
cronjob_manage(
    action="create",
    schedule="50 18 * * 1",       # 18:50 toda segunda-feira
    name="checar-salas-meet-segunda",
    command="cd /caminho/para/ti-ajuda-eti && .venv/bin/python3 scripts/checar_salas_meet.py --csv config/salas.csv --dia segunda",
    deliver="telegram",            # ou outro canal configurado no seu gateway
)
```

Ajuste `schedule` (expressão cron, fuso do agendador) e `deliver` conforme
o canal de notificação disponível no seu ambiente Hermes. Depois de criar,
sempre dispare um `run` manual e confirme sucesso antes de confiar no
agendamento automático.

## Pitfalls gerais (vale tanto para crontab quanto para Hermes)

- O token OAuth expira e é renovado automaticamente pelos scripts (via
  refresh_token) — mas o refresh_token em si pode ser revogado se a conta
  trocar de senha, remover o acesso do app, ou se o app OAuth estiver em
  modo de teste no Google Cloud Console (esses tokens expiram em 7 dias).
  Para produção/uso contínuo, publique o app OAuth (ou use uma conta
  Workspace com o app marcado como "Interno").
- Não agende verificações de Meet API com intervalo muito curto (ex.:
  abaixo de 30-60s) se estiver checando muitas salas de uma vez — pode
  esbarrar em cota/rate limit do Google.
