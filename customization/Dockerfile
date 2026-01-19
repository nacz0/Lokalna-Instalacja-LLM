# Custom Open WebUI z własnymi stylami CSS i JavaScript
FROM ghcr.io/open-webui/open-webui:main

# Kopiuj niestandardowy CSS do kontenera (do katalogu build, aby był dostępny)
COPY custom.css /app/build/custom.css

# Kopiuj routing script dla pipeline'ów
COPY pipeline-routing.js /app/build/pipeline-routing.js

# Wstrzyknij link do custom.css i script w index.html
RUN sed -i 's|</head>|<link rel="stylesheet" href="/custom.css">\n  <script src="/pipeline-routing.js"><\/script>\n</head>|' /app/build/index.html
