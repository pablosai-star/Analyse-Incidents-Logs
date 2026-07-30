# Analyse d'Incidents Logs

Outil Python d'analyse de logs applicatifs, avec détection automatique des incidents critiques et intégration à une plateforme d'observabilité (Datadog).

## Contexte

Projet réalisé dans le cadre d'une montée en compétence sur les outils d'observabilité (Datadog/Kibana) et le scripting d'analyse d'incidents, pour un poste de Référent Support Applicatif.

Le script simule un cas d'usage réaliste : l'analyse de logs d'une plateforme de services bancaires (signature EBICS, prélèvements, flux bancaires) pour identifier rapidement les incidents nécessitant une intervention prioritaire.

## Fonctionnalités

- **Chargement** de logs au format JSON Lines (`.jsonl`)
- **Agrégation** des erreurs par service et par client
- **Reconstruction chronologique** d'un incident pour un client donné (facilite la reproduction du problème)
- **Détection automatique d'escalade** : identifie les clients à surveiller en priorité (nombre d'erreurs élevé + présence d'un log `CRITICAL`)
- **Génération de rapports** au format texte (lisible) et CSV (exploitable dans Excel/Power BI)
- **Envoi vers Datadog** via l'API Logs (`/api/v2/logs`), pour visualisation dans le Log Explorer et déclenchement de monitors/alertes
- **Reproduction d'incident en bash** : script complémentaire qui isole les logs d'un client précis et génère les commandes de rejeu correspondantes

## Structure du projet

├── Analyse-Incidents-Logs.py   # Script principal (Python)
├── Dashboard_KIBANA_4_indicators.png
├── README.md
├── app.log
├── app.timestamped.log
├── check_api.sh
├── detection_pic.sh
├── rapport.sh
├── rapport_incidents.csv       # Export utilisé par le script bash
├── reproduire_incident.sh      # Script de reproduction d'incident (Bash)
├── sample_logs.jsonl                  # Jeu de logs d'exemple (données fictives)
└── .gitignore


## Installation

```bash
pip install requests python-dotenv
```

Crée un fichier `.env` à la racine du projet (non versionné) :

```
DATADOG_API_KEY=ta_cle_api
DATADOG_SITE=datadoghq.eu
```

## Utilisation

```bash
python Analyse-Incidents-Logs.py --input logs.jsonl
```

Le script affiche dans la console :
- Le nombre de logs chargés
- Les erreurs agrégées par service et par client
- La liste des clients à surveiller en priorité
- La chronologie détaillée de chaque incident détecté

Il génère également deux rapports (`rapport_incidents.txt` et `.csv`) et envoie les logs vers Datadog pour exploitation dans le Log Explorer.

## Exemple de sortie

```
20 logs chargés
Erreurs par service : {'ebics-signature-service': 3, 'auth-service': 3, 'directdebit-service': 5}
Erreurs par client  : {45892: 3, 31220: 3, 50213: 5}
Clients à surveiller en priorité : [50213]

--- Chronologie du client 50213 ---
2026-07-22T09:05:48Z - CRITICAL - Timeout connexion passerelle bancaire
2026-07-22T09:14:39Z - ERROR - Timeout connexion passerelle bancaire
...
```

## Côté observabilité

Les logs envoyés à Datadog peuvent être filtrés via une requête simple dans le Log Explorer :

```
service:directdebit-service (status:error OR status:critical)
```

Un monitor a été configuré sur cette requête pour déclencher une alerte automatique (email) dès qu'un seuil d'erreurs est dépassé sur une fenêtre de 10 minutes — reproduisant un scénario réel de supervision applicative.

## Reproduction d'incident (Bash)

Le script `reproduire_incident.sh` isole les logs d'un client donné à partir du rapport CSV et génère les commandes de rejeu correspondantes (requêtes `curl` simulées vers le service concerné).

\```bash
bash reproduire_incident.sh <client_id>
\```

Exemple :
\```bash
bash reproduire_incident.sh 50213
\```

\```
--- Rejeu de l'incident : 2026-07-22T09:05:48Z ---
curl -X POST https://api-interne/directdebit-service/replay \
  -H 'Content-Type: application/json' \
  -d '{"client_id": "50213", "bank": "LCL", "original_status": "504"}'
\```

Le script utilise `IFS` pour parser le CSV champ par champ, et nettoie les retours chariot (`tr -d '\r'`) pour rester compatible avec des fichiers générés sous Windows.



# Analyse des incidents LOG

Scripts Bash d'analyse et de supervision de logs applicatifs.

## Scripts

| Fichier | Description |
|--------|-------------|
| `rapport.sh` | Génère un rapport d'incident à partir d'un fichier log |
| `detection_pic.sh` | Détecte les pics d'erreurs par tranche de temps |
| `surveillance.sh` | Surveille un log en temps réel et alerte selon un seuil |

## Utilisation

```bash
./rapport.sh
./detection_pic.sh
./surveillance.sh
```

## Environnement
- Bash / Git Bash (Windows)
- Logs applicatifs structurés avec niveaux INFO / ERROR / DEBUG

  

## Check_api.sh — Vérification et test d'API REST

Script bash pour tester et diagnostiquer des endpoints d'API REST : requêtes GET/POST, vérification des codes de statut HTTP, et mode debug pour l'inspection détaillée des réponses.

Fonctionnalités :

Requêtes GET et POST via curl
Vérification automatique des codes de statut HTTP (200, 404, 500...)
Mode debug pour afficher headers et corps de réponse en détail
Testé sur l'API publique JSONPlaceholder dans le cadre d'une formation Web Services (HTTP, curl, Postman)

Usage :

bash
./check_api.sh <url> [--post] [--debug]

Contexte : ce script s'inscrit dans la continuité des outils de supervision applicative du dépôt (rapport.sh, detection_pic.sh, surveillance.sh) — même logique de diagnostic automatisé, appliquée cette fois aux échanges API plutôt qu'aux logs applicatifs.

## Exemple indicateurs Dashboard Datadog
  <img width="1719" height="828" alt="image" src="https://github.com/user-attachments/assets/f75069ed-3a57-4343-8f02-22372382297c" />

-C'est un dashboard complet et cohérent, qui répond à 4 questions différentes qu'un support se pose face à un incident : "ça évolue comment dans le temps", "qui est le plus touché", "combien de critique en tout", "qu'est-ce qui se passe précisément"

  
## Pistes d'évolution

- Détection d'anomalies par comparaison à une baseline historique
- Export automatique des rapports vers un espace partagé (Slack, email)


