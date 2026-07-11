# Single, self-contained "study" image for the learn-by-doing platform.
#
# Bundles: the Streamlit learning app + an embedded Postgres warehouse (so the
# SQL / ingestion / dbt-style / serving / security / architecture tasks grade)
# + a Java 17 runtime and PySpark (so the Spark / real-time / structured-
# streaming tasks grade). The ~50 pure-Python (pyfunc) tasks need nothing extra.
#
# Progress, your submitted code, and the warehouse data all live under
# /app/state, which is a named volume — so nothing is lost when the container
# stops. Build once, study anytime:
#
#   docker build -t learn-de .
#   docker run -d -p 8501:8501 -v learn-de-state:/app/state --name learn-de learn-de
#   open http://localhost:8501
#
# A few tool-specific tasks (real dbt build, live Airflow DAGs, the Redpanda
# broker) still need the full docker-compose stack — see the README.

FROM python:3.11-slim-bookworm

# System deps: embedded Postgres warehouse + a Java runtime for Spark.
RUN apt-get update && apt-get install -y --no-install-recommends \
        postgresql postgresql-client \
        openjdk-17-jre-headless \
        procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first so the layer caches across app-code changes.
COPY platform/requirements.txt platform/requirements.txt
RUN pip install --no-cache-dir -r platform/requirements.txt

# App code.
COPY . /app
RUN chmod +x /app/docker-entrypoint.sh

ENV POSTGRES_HOST=127.0.0.1 \
    POSTGRES_PORT=5432 \
    POSTGRES_DB=datamart \
    POSTGRES_USER=airflow \
    POSTGRES_PASSWORD=airflow \
    PYTHONPATH=/app/platform \
    PGDATA=/app/state/pgdata \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Everything that must survive a power-down lives here.
VOLUME ["/app/state"]
EXPOSE 8501

# Report healthy once the app is actually serving (allow time for first-boot
# Postgres init). Uses Streamlit's built-in health endpoint; no extra tooling.
HEALTHCHECK --interval=15s --timeout=5s --start-period=45s --retries=5 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3).status==200 else 1)"

ENTRYPOINT ["/app/docker-entrypoint.sh"]
