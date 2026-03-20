#!/bin/sh

# Ta część generuje plik env-config.js na podstawie zmiennych środowiskowych kontenera.
# Zostanie on umieszczony w folderze publicznym serwera Nginx.
echo "window._env_ = {" > /usr/share/nginx/html/env-config.js
echo "  VITE_API_URL: \"$VITE_API_URL\"," >> /usr/share/nginx/html/env-config.js
echo "  VITE_GOOGLE_CLIENT_ID: \"$VITE_GOOGLE_CLIENT_ID\"" >> /usr/share/nginx/html/env-config.js
echo "};" >> /usr/share/nginx/html/env-config.js

# Uruchamia Nginx w trybie normalnym
exec "$@"
