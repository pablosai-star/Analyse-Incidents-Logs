#!/bin/bash

FICHIER="app_timestamped.log"
SEUIL=3

echo "=== Détection de pic d'erreurs ==="
echo ""

# Extraire les minutes où il y a des erreurs
echo "--- Erreurs par minute ---"
grep "ERROR" $FICHIER | awk '{print $2}' | cut -d: -f1,2 | sort | uniq -c

echo ""

# Chercher si une minute dépasse le seuil
pic=$(grep "ERROR" $FICHIER | awk '{print $2}' | cut -d: -f1,2 | sort | uniq -c | awk -v seuil=$SEUIL '$1 >= seuil {print $1, "erreurs à", $2}')

if [ -n "$pic" ]; then
    echo "⚠ PIC DÉTECTÉ : $pic"
else
    echo "✓ Pas de pic détecté"
fi