#!/bin/bash

FICHIER="app.log"
DATE=$(date '+%Y-%m-%d %H:%M')

echo "============================="
echo "  RAPPORT D'INCIDENT"
echo "  Généré le : $DATE"
echo "============================="
echo ""

# Comptage par niveau
for niveau in INFO ERROR DEBUG; do
    nb=$(grep -c "$niveau" $FICHIER)
    echo "$niveau : $nb occurrences"
done

echo ""

# Détail des erreurs
echo "--- Détail des erreurs ---"
grep "ERROR" $FICHIER

echo ""

# Conclusion
nb_erreurs=$(grep -c "ERROR" $FICHIER)
if [ $nb_erreurs -gt 3 ]; then
    echo "⚠ STATUT : Anomalie détectée — $nb_erreurs erreurs"
else
    echo "✓ STATUT : Nominal"
fi