FROM ghcr.io/open-webui/pipelines:main@sha256:b48e9bc338ce2be0acfbeff01810db72408a12f07739f9e3879c1f2b00952d6e

COPY pipelines/requirements.txt /app/pipelines/requirements.txt
RUN pip install --no-cache-dir -r /app/pipelines/requirements.txt

COPY pipelines/ /app/pipelines/
COPY integrations/ /app/integrations/
