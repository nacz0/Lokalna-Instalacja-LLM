# Custom Open WebUI z własnymi stylami CSS
FROM ghcr.io/open-webui/open-webui:main

# Kopiuj niestandardowy CSS do kontenera (do katalogu build, aby był dostępny)
COPY custom.css /app/build/custom.css

# Wstrzyknij link do custom.css w index.html
RUN sed -i 's|</head>|<link rel="stylesheet" href="/custom.css"></head>|' /app/build/index.html
