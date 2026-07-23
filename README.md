# Analyse-Incidents-Logs
Python tool for analyzing application logs (.jsonl): automatic client incident detection via error counting, timeline reconstruction, and critical-case flagging. Generates text and CSV reports.

FR:
Outil Python d'analyse de logs applicatifs (.jsonl) : détection automatique des incidents clients par comptage d'erreurs, reconstruction de chronologie et repérage des cas critiques. Génère des rapports texte et CSV.

Topics (tags GitHub): python logging observability incident-management data-analysis cli

# Analyse d'incidents applicatifs (logs JSON Lines)

Outil en Python pur (sans dépendance externe) pour analyser des logs applicatifs
au format `.jsonl` et repérer automatiquement les clients à surveiller en cas
d'incident (paiement en échec, erreurs répétées, etc.).

## Contexte

Dans un contexte de support applicatif / observabilité, les logs bruts sont
souvent trop volumineux pour être lus manuellement. Ce script automatise
trois tâches courantes :

- **Comptage** des erreurs (`ERROR` / `CRITICAL`) par service et par client
- **Reconstruction chronologique** d'un incident pour un client donné
  (rejouer la séquence d'événements)
- **Détection d'escalade** : identifier les clients dont le nombre d'erreurs
  dépasse un seuil ET qui ont au moins une erreur `CRITICAL`, pour prioriser
  le traitement

## Fonctionnalités

- Chargement robuste d'un fichier `.jsonl` (les lignes invalides sont
  ignorées avec un avertissement, sans faire planter le script)
- Génération d'un **rapport texte** lisible (compte-rendu d'incident)
- Export **CSV** exploitable dans Excel / Power BI
- Interface en ligne de commande (seuil et fichier d'entrée configurables)

## Structure du projet

```
.
├── analyse_incidents.py     # Script principal
├── data/
│   └── sample_logs.jsonl    # Jeu de données d'exemple (16 logs, 2 scénarios d'incident)
├── requirements.txt
└── README.md
```

## Installation

Aucune dépendance externe : seule la bibliothèque standard de Python (3.10+)
est utilisée.

```bash
git clone https://github.com/pablosai-star/Analyse-Incidents-Logs.git
cd Analyse-Incidents-Logs
```

## Utilisation

```bash
# Avec les données d'exemple fournies
python analyse_incidents.py --input data/sample_logs.jsonl

# Avec un seuil d'escalade personnalisé (par défaut : 3 erreurs)
python analyse_incidents.py --input data/sample_logs.jsonl --seuil 5

# Avec un préfixe de sortie personnalisé
python analyse_incidents.py --input data/sample_logs.jsonl --output-prefix rapport_mars
```

Le script génère deux fichiers dans le dossier courant :
- `rapport_incidents.txt` : compte-rendu lisible avec la chronologie des
  clients suspects
- `rapport_incidents.csv` : export brut de tous les logs

## Format d'entrée attendu

Chaque ligne du fichier `.jsonl` est un objet JSON avec les clés suivantes :

```json
{
    "timestamp": "2024-03-01T10:15:00+00:00",
    "level": "ERROR",
    "service": "payments-api",
    "message": "Timeout while calling bank gateway",
    "client_id": 1042,
    "bank": "BNP",
    "status_code": 504
}
```
