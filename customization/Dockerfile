# Custom Open WebUI z własnymi stylami CSS i JavaScript
FROM ghcr.io/open-webui/open-webui:v0.9.5@sha256:e045bde3b004cc7f8c319412345eb56c87ea6ac57031534a31ca37ad5424beb3

# Kopiuj niestandardowy CSS do kontenera (do katalogu build, aby był dostępny)
COPY custom.css /app/build/custom.css

# Kopiuj routing script dla pipeline'ów
COPY pipeline-routing.js /app/build/pipeline-routing.js

# Kopiuj Spotify authentication check
COPY spotify-auth-check.js /app/build/spotify-auth-check.js

# Wstrzyknij linki do custom.css i scriptow w index.html
RUN sed -i 's|</head>|<link rel="stylesheet" href="/custom.css">\n  <script src="/pipeline-routing.js"><\/script>\n  <script src="/spotify-auth-check.js"><\/script>\n</head>|' /app/build/index.html
