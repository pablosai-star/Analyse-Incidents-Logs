#!/bin/bash

URL="https://jsonplaceholder.typicode.com/posts/1"

code=$(curl -o /dev/null -s -w "%{http_code}" $URL)

if [ "$code" == "200" ]; then
    echo "✅ Service OK — code $code"
else
    echo "🚨 ALERTE — code $code sur $URL"
fi