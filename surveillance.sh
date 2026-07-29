#!/bin/bash

FICHIER="app_timestamped.log"
SEUIL=2
compteur=0

echo "=== Surveillance en temps réel ==="
echo "Fichier : $FICHIER"
echo "Seuil d'alerte : $SEUIL erreurs"
echo "En attente d'événements... (Ctrl+C pour arrêter)"
echo ""

tail -f $FICHIER | while read ligne; do

    echo "[LOG] $ligne"

    # Si la ligne contient ERROR
    if echo "$ligne" | grep -q "ERROR"; then
        compteur=$((compteur + 1))
        echo "  ⚠ Erreur détectée ($compteur/$SEUIL)"

        if [ $compteur -ge $SEUIL ]; then
            echo "  🚨 ALERTE : seuil atteint — intervention requise"
            compteur=0  # reset après alerte
        fi
    fi

done