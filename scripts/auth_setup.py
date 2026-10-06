#!/usr/bin/env python3
"""Gera/renova o token OAuth local usado pelos demais scripts.

Uso:
    python3 scripts/auth_setup.py

Pede um login interativo (abre o navegador local; em ambiente sem
navegador, imprime uma URL para abrir manualmente e colar o código de
retorno) e salva o token em config/token.json (caminho definido em
config/config.yaml -> google.token_path).
"""
from __future__ import annotations

import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

sys.path.insert(0, str(Path(__file__).resolve().parent))
from google_auth import CONFIG_PATH, load_config  # noqa: E402


def main() -> None:
    config = load_config()
    client_secret_path = Path(config["google"]["client_secret_path"])
    if not client_secret_path.is_absolute():
        client_secret_path = CONFIG_PATH.parent.parent / client_secret_path

    if not client_secret_path.exists():
        print(
            f"Client secret não encontrado em {client_secret_path}.\n"
            "Veja docs/oauth_setup.md para criar um OAuth client ID "
            "(tipo 'Desktop app') no Google Cloud Console e baixar o JSON."
        )
        sys.exit(1)

    scopes = config["google"]["scopes"]
    flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_path), scopes)

    # run_local_server abre o navegador e sobe um servidor local para
    # capturar o redirect OAuth. Em ambiente sem navegador/GUI, use
    # flow.run_console() no lugar (requer copiar/colar o código manualmente).
    creds = flow.run_local_server(port=0)

    token_path = Path(config["google"]["token_path"])
    if not token_path.is_absolute():
        token_path = CONFIG_PATH.parent.parent / token_path
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json(), encoding="utf-8")

    print(f"Token salvo em {token_path}.")
    print("Pronto — os demais scripts já podem usar essas credenciais.")


if __name__ == "__main__":
    main()
