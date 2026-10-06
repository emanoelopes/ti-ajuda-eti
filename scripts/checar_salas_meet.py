#!/usr/bin/env python3
"""Checa o status das salas Google Meet listadas num CSV: ativa/inativa,
número de participantes e se está gravando. Útil para validar, antes do
início de um encontro, que todos os links do plantão estão corretos e
funcionando (sem precisar entrar manualmente em cada sala).

Uso:
    python3 scripts/checar_salas_meet.py --csv config/salas.csv
    python3 scripts/checar_salas_meet.py --csv config/salas.csv --dia segunda

Formato esperado do CSV (ver config/salas.example.csv):
    nome,dia_semana,link_meet
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from google_auth import get_credentials, load_config  # noqa: E402

MEET_CODE_RE = re.compile(r"([a-z]{3}-[a-z]{4}-[a-z]{3})")
MEET_API_BASE = "https://meet.googleapis.com/v2"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv", help="Caminho do CSV de salas (default: config.yaml -> salas.csv_path)")
    p.add_argument("--dia", help="Filtra só salas desse dia_semana (ex.: segunda)")
    return p.parse_args()


def meet_code_from_link(link: str) -> str | None:
    m = MEET_CODE_RE.search(link)
    return m.group(1) if m else None


def get_space(session: requests.Session, meeting_code: str) -> dict | None:
    resp = session.get(f"{MEET_API_BASE}/spaces/{meeting_code}")
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def count_participants(session: requests.Session, conference_record: str) -> int:
    total = 0
    page_token = None
    while True:
        params = {"pageSize": 250, "filter": "latest_end_time IS NULL"}
        if page_token:
            params["pageToken"] = page_token
        resp = session.get(f"{MEET_API_BASE}/{conference_record}/participants", params=params)
        resp.raise_for_status()
        data = resp.json()
        total += len(data.get("participants", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return total


def is_recording(session: requests.Session, conference_record: str) -> bool:
    resp = session.get(f"{MEET_API_BASE}/{conference_record}/recordings")
    resp.raise_for_status()
    recs = resp.json().get("recordings", [])
    return any(r.get("state") == "STARTED" for r in recs)


def main() -> None:
    args = parse_args()
    config = load_config()
    csv_path = Path(args.csv or config["salas"]["csv_path"])
    if not csv_path.is_absolute():
        csv_path = Path(__file__).resolve().parent.parent / csv_path

    if not csv_path.exists():
        print(f"CSV não encontrado em {csv_path}. Veja config/salas.example.csv.")
        sys.exit(1)

    creds = get_credentials(config)
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {creds.token}"})

    with csv_path.open(encoding="utf-8") as f:
        salas = list(csv.DictReader(f))

    if args.dia:
        salas = [s for s in salas if s.get("dia_semana", "").lower() == args.dia.lower()]

    if not salas:
        print("Nenhuma sala para checar (confira --dia ou o conteúdo do CSV).")
        return

    print(f"Checando {len(salas)} sala(s)...\n")
    problemas = []

    for sala in salas:
        nome = sala["nome"]
        link = sala["link_meet"]
        code = meet_code_from_link(link)
        if not code:
            print(f"[ERRO] {nome}: link sem código de reunião válido: {link}")
            problemas.append(nome)
            continue

        try:
            space = get_space(session, code)
        except requests.HTTPError as e:
            print(f"[ERRO] {nome}: falha ao consultar Meet API ({e})")
            problemas.append(nome)
            continue

        if space is None:
            print(f"[ERRO] {nome}: código '{code}' não existe (link quebrado/errado)")
            problemas.append(nome)
            continue

        active = space.get("activeConference")
        if not active:
            print(f"[ok]   {nome}: link válido, sala inativa no momento")
            continue

        conference_record = active["conferenceRecord"]
        n_part = count_participants(session, conference_record)
        gravando = is_recording(session, conference_record)
        print(
            f"[ok]   {nome}: ATIVA — {n_part} participante(s)"
            f"{' — GRAVANDO' if gravando else ''}"
        )

    print()
    if problemas:
        print(f"{len(problemas)} sala(s) com problema: {', '.join(problemas)}")
        sys.exit(1)
    print("Todas as salas checadas sem erros de link.")


if __name__ == "__main__":
    main()
