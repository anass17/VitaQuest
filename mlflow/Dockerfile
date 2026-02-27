FROM ghcr.io/mlflow/mlflow:v3.8.1


WORKDIR /app
COPY ./mlflow .


# Install PostgreSQL driver
RUN pip install psycopg2-binary


CMD mlflow server \
    --backend-store-uri $BACKEND_URI \
    --default-artifact-root /mlflow/artifacts \
    --serve-artifacts \
    --host 0.0.0.0 \
    --port 5000 \
    --allowed-hosts "*"