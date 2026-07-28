#!/bin/bash

fichier="rapport_incidents.csv"
client_cible="$1"

if [ -z "$client_cible" ]; then
    echo "Usage : ./reproduire_incident.sh <client_id>"
    exit 1
fi

tr -d '\r' < "$fichier" | tail -n +2 | while IFS=',' read -r timestamp level service message client_id bank status_code
do
    if [ "$client_id" == "$client_cible" ]; then
        echo "--- Rejeu de l'incident : $timestamp ---"
        echo "curl -X POST https://api-interne/$service/replay \\"
        echo "  -H 'Content-Type: application/json' \\"
        echo "  -d '{\"client_id\": \"$client_id\", \"bank\": \"$bank\", \"original_status\": \"$status_code\"}'"
        echo ""
    fi
done