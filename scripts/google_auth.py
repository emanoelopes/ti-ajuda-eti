"""Helper de carregamento/refresh de credenciais OAuth para os scripts do
TI Ajuda ETI.

Lê sempre os escopos gravados no PRÓPRIO arquivo de token (campo "scopes"),
nunca uma lista fixa no código — se o token tiver sido autorizado com um
conjunto de escopos diferente do esperado, forçar escopos "fixos" no código
quebra o refresh com `invalid_scope`.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "config.yaml"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Config não encontrada em {CONFIG_PATH}. "
            "Copie config/config.example.yaml para config/config.yaml e preencha."
        )
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_credentials(config: dict | None = None) -> Credentials:
    """Carrega e, se necessário, renova as credenciais OAuth do usuário.

    Sempre lê os escopos do próprio arquivo de token (não um conjunto fixo),
    para evitar RefreshError: invalid_scope quando o token foi autorizado
    com escopos diferentes dos esperados pelo script atual.
    """
    config = config or load_config()
    token_path = Path(config["google"]["token_path"])
    if not token_path.is_absolute():
        token_path = CONFIG_PATH.parent.parent / token_path

    if not token_path.exists():
        raise FileNotFoundError(
            f"Token não encontrado em {token_path}. Rode primeiro: "
            "python3 scripts/auth_setup.py"
        )

    raw = json.loads(token_path.read_text(encoding="utf-8"))
    scopes = raw.get("scopes") or config["google"]["scopes"]
    creds = Credentials.from_authorized_user_info(raw, scopes)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json(), encoding="utf-8")

    if not creds.valid:
        raise RuntimeError(
            "Credenciais inválidas e sem refresh_token utilizável. "
            "Reautorize com: python3 scripts/auth_setup.py"
        )
    return creds
