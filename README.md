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

## Structure du projet

```
├── Analyse-Incidents-Logs.py   # Script principal
├── logs.jsonl                  # Jeu de logs d'exemple (données fictives)
├── .gitignore
└── README.md
```

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

## Pistes d'évolution

- Détection d'anomalies par comparaison à une baseline historique
- Dashboard Datadog dédié (metrics + logs + monitors sur une seule vue)
- Export automatique des rapports vers un espace partagé (Slack, email)
