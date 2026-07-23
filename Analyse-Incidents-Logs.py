"""
analyse_incidents.py

Outil d'analyse de logs applicatifs au format JSON Lines (.jsonl).

Fonctionnalités :
    - chargement d'un fichier de logs (.jsonl)
    - comptage des erreurs par service et par client
    - reconstruction de la chronologie d'un incident pour un client donné
    - détection automatique des clients à surveiller en priorité
    - génération d'un rapport texte (compte-rendu) et d'un export CSV

Usage :
    python analyse_incidents.py --input data/sample_logs.jsonl
    python analyse_incidents.py --input data/sample_logs.jsonl --seuil 5

Format attendu pour chaque ligne du fichier .jsonl :
    {
        "timestamp": "2024-03-01T10:15:00+00:00",
        "level": "ERROR",
        "service": "payments-api",
        "message": "Timeout while calling bank gateway",
        "client_id": 1042,
        "bank": "BNP",
        "status_code": 504
    }
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

NIVEAUX_ERREUR = ("ERROR", "CRITICAL")
COLONNES_CSV = ["timestamp", "level", "service", "message", "client_id", "bank", "status_code"]


def charger_logs(chemin_fichier: str | Path) -> list[dict[str, Any]]:
    """
    Charge un fichier de logs au format JSON Lines (une ligne = un objet JSON).

    Args:
        chemin_fichier: chemin vers le fichier .jsonl

    Returns:
        Liste des logs, chacun sous forme de dictionnaire.

    Raises:
        FileNotFoundError: si le fichier n'existe pas.
    """
    chemin_fichier = Path(chemin_fichier)
    if not chemin_fichier.exists():
        raise FileNotFoundError(f"Fichier introuvable : {chemin_fichier}")

    logs = []
    with chemin_fichier.open("r", encoding="utf-8") as f:
        for numero_ligne, ligne in enumerate(f, start=1):
            ligne = ligne.strip()
            if not ligne:
                continue  # ignore les lignes vides
            try:
                logs.append(json.loads(ligne))
            except json.JSONDecodeError as e:
                logger.warning("Ligne %d ignorée (JSON invalide) : %s", numero_ligne, e)
    return logs


def analyser_erreurs(logs: list[dict[str, Any]]) -> tuple[dict[str, int], dict[Any, int]]:
    """
    Compte le nombre d'erreurs (ERROR ou CRITICAL) par service et par client.

    Args:
        logs: liste des logs chargés

    Returns:
        Tuple (erreurs_par_service, erreurs_par_client).
    """
    erreurs_par_service: dict[str, int] = defaultdict(int)
    erreurs_par_client: dict[Any, int] = defaultdict(int)

    for log in logs:
        if log.get("level") not in NIVEAUX_ERREUR:
            continue
        service = log.get("service")
        client_id = log.get("client_id")
        if service is None or client_id is None:
            logger.warning("Log ignoré (service ou client_id manquant) : %s", log)
            continue
        erreurs_par_service[service] += 1
        erreurs_par_client[client_id] += 1

    return erreurs_par_service, erreurs_par_client


def chronologie_client(logs: list[dict[str, Any]], client_id_cible: Any) -> list[dict[str, Any]]:
    """
    Extrait tous les logs d'un client donné, dans l'ordre chronologique
    (utile pour "rejouer" la séquence d'un incident).

    Args:
        logs: liste des logs chargés
        client_id_cible: identifiant du client à isoler

    Returns:
        Logs du client, triés par timestamp.
    """
    logs_client = [log for log in logs if log.get("client_id") == client_id_cible]
    logs_client.sort(key=lambda log: log.get("timestamp", ""))
    return logs_client


def detecter_escalade(
    logs: list[dict[str, Any]],
    erreurs_par_client: dict[Any, int],
    seuil: int = 3,
) -> list[Any]:
    """
    Repère les clients dont le nombre d'erreurs dépasse un seuil
    ET qui ont au moins un log CRITICAL (pas juste du bruit).

    Args:
        logs: liste des logs chargés
        erreurs_par_client: résultat de analyser_erreurs()
        seuil: nombre minimum d'erreurs pour être suspecté

    Returns:
        Identifiants des clients à surveiller en priorité.
    """
    clients_a_surveiller = []

    for client_id, nb_erreurs in erreurs_par_client.items():
        if nb_erreurs < seuil:
            continue
        logs_du_client = chronologie_client(logs, client_id)
        a_du_critical = any(log.get("level") == "CRITICAL" for log in logs_du_client)
        if a_du_critical:
            clients_a_surveiller.append(client_id)

    return clients_a_surveiller


def generer_rapport_texte(
    logs: list[dict[str, Any]],
    erreurs_par_service: dict[str, int],
    erreurs_par_client: dict[Any, int],
    suspects: list[Any],
    chemin_sortie: str | Path = "rapport_incidents.txt",
) -> None:
    """Génère un rapport texte lisible, façon compte-rendu d'incident."""
    from datetime import datetime, timezone

    chemin_sortie = Path(chemin_sortie)
    with chemin_sortie.open("w", encoding="utf-8") as f:
        f.write("RAPPORT D'ANALYSE D'INCIDENTS\n")
        f.write(f"Genere le : {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"Nombre total de logs analyses : {len(logs)}\n")
        f.write("=" * 50 + "\n\n")

        f.write("Erreurs par service :\n")
        for service, nb in erreurs_par_service.items():
            f.write(f"  - {service} : {nb}\n")

        f.write("\nErreurs par client :\n")
        for client_id, nb in erreurs_par_client.items():
            f.write(f"  - Client {client_id} : {nb}\n")

        f.write("\nClients a surveiller en priorite :\n")
        if not suspects:
            f.write("  Aucun\n")
        else:
            for client_id in suspects:
                f.write(f"  - Client {client_id}\n")

        for client_id in suspects:
            f.write(f"\n  --- Chronologie du client {client_id} ---\n")
            for log in chronologie_client(logs, client_id):
                f.write(f"  {log.get('timestamp')} - {log.get('level')} - {log.get('message')}\n")

    logger.info("Rapport texte genere : %s", chemin_sortie)


def generer_rapport_csv(logs: list[dict[str, Any]], chemin_sortie: str | Path = "rapport_incidents.csv") -> None:
    """Génère un export CSV brut de tous les logs, exploitable dans Excel/Power BI."""
    chemin_sortie = Path(chemin_sortie)
    with chemin_sortie.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLONNES_CSV)
        writer.writeheader()
        for log in logs:
            writer.writerow({col: log.get(col, "") for col in COLONNES_CSV})

    logger.info("Rapport CSV genere : %s", chemin_sortie)


def parse_args() -> argparse.Namespace:
    """Définit et parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Analyse des logs applicatifs (.jsonl) pour détecter des incidents client."
    )
    parser.add_argument(
        "--input",
        "-i",
        default="data/sample_logs.jsonl",
        help="Chemin vers le fichier de logs .jsonl (défaut : data/sample_logs.jsonl)",
    )
    parser.add_argument(
        "--seuil",
        "-s",
        type=int,
        default=3,
        help="Nombre minimum d'erreurs pour qu'un client soit suspecté (défaut : 3)",
    )
    parser.add_argument(
        "--output-prefix",
        "-o",
        default="rapport_incidents",
        help="Préfixe des fichiers de rapport générés (défaut : rapport_incidents)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    logs = charger_logs(args.input)
    logger.info("%d logs chargés", len(logs))

    erreurs_par_service, erreurs_par_client = analyser_erreurs(logs)
    logger.info("Erreurs par service : %s", dict(erreurs_par_service))
    logger.info("Erreurs par client  : %s", dict(erreurs_par_client))

    suspects = detecter_escalade(logs, erreurs_par_client, seuil=args.seuil)
    logger.info("Clients à surveiller en priorité : %s", suspects)

    for client_id in suspects:
        print(f"\n--- Chronologie du client {client_id} ---")
        for log in chronologie_client(logs, client_id):
            print(f"{log.get('timestamp')} - {log.get('level')} - {log.get('message')}")

    generer_rapport_texte(
        logs,
        erreurs_par_service,
        erreurs_par_client,
        suspects,
        chemin_sortie=f"{args.output_prefix}.txt",
    )
    generer_rapport_csv(logs, chemin_sortie=f"{args.output_prefix}.csv")


if __name__ == "__main__":
    main()