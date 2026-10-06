#!/usr/bin/env python3
"""Checa gravações de um encontro no Google Drive e, opcionalmente, abre a
permissão de compartilhamento ("qualquer pessoa com o link" / leitor).

Uso:
    python3 scripts/verificar_gravacoes.py --sala BS4 --desde 2026-09-16
    python3 scripts/verificar_gravacoes.py --sala BS4 --desde 2026-09-16 --abrir-permissao

A tag passada em --sala é usada para filtrar arquivos cujo nome a contenha
(ex.: "BS4", "CS1") — ajuste config/config.yaml -> drive.nome_contem se o
padrão de nomenclatura do seu Drive for diferente de "{TAG}".
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from googleapiclient.discovery import build

sys.path.insert(0, str(Path(__file__).resolve().parent))
from google_auth import get_credentials, load_config  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sala", required=True, help="Tag/identificador da sala (ex.: BS4, CS1)")
    p.add_argument("--desde", required=True, help="Data mínima de modificação, formato AAAA-MM-DD")
    p.add_argument(
        "--abrir-permissao",
        action="store_true",
        help="Se um arquivo não tiver permissão 'qualquer pessoa com o link', cria uma (role=reader)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    creds = get_credentials(config)
    drive = build("drive", "v3", credentials=creds)

    nome_padrao = config["drive"]["nome_contem"].format(TAG=args.sala)
    query_parts = [
        f"name contains '{nome_padrao}'",
        "mimeType contains 'video'",
        f"modifiedTime > '{args.desde}T00:00:00'",
    ]
    pasta_id = config["drive"].get("pasta_id")
    if pasta_id:
        query_parts.append(f"'{pasta_id}' in parents")
    query = " and ".join(query_parts)

    resp = drive.files().list(
        q=query,
        fields="files(id,name,modifiedTime,webViewLink)",
        orderBy="modifiedTime",
        pageSize=100,
    ).execute()
    files = resp.get("files", [])

    if not files:
        print(f"Nenhuma gravação encontrada para '{args.sala}' desde {args.desde}.")
        return

    print(f"{len(files)} gravação(ões) encontrada(s) para '{args.sala}' desde {args.desde}:\n")
    for f in files:
        perms = drive.permissions().list(
            fileId=f["id"], fields="permissions(id,type,role)"
        ).execute().get("permissions", [])
        aberto = any(p.get("type") == "anyone" for p in perms)

        status = "ABERTO (anyone/reader ou superior)" if aberto else "FECHADO (precisa compartilhar)"
        print(f"- {f['name']}")
        print(f"  modificado em: {f['modifiedTime']}")
        print(f"  link: {f.get('webViewLink', '(sem link)')}")
        print(f"  permissão: {status}")

        if not aberto and args.abrir_permissao:
            drive.permissions().create(
                fileId=f["id"], body={"type": "anyone", "role": "reader"}
            ).execute()
            print("  -> permissão 'anyone/reader' criada agora.")
        print()


if __name__ == "__main__":
    main()
