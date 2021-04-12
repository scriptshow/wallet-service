FROM python:3.9-alpine

ENV WALLET_SERVICE_DEBUG_MODE 'False'
ENV WALLET_SERVICE_LOG_LEVEL 'info'
ENV WALLET_SERVICE_SECRET_KEY 'SECRET_KEY_HERE'
ENV WALLET_SERVICE_ALLOWED_HOSTS 'localhost 127.0.0.1'
ENV WALLET_SERVICE_ALLOWED_ORIGINS 'http://localhost:8000 http://127.0.0.1:8000'
# Expiration time in hours
ENV WALLET_SERVICE_AUTH_TOKEN_EXPIRATION '2'
# Max number of wallet creation allowed for clients, if 0 = unlimited
ENV WALLET_SERVICE_MAX_WALLETS_BY_CLIENT '0'

# Recommended value: (2 * CPU_NUM) + 1
ENV WALLET_SERVICE_WORKERS '5'

# Database configuration
ENV POSTGRES_DB_NAME 'DB_NAME'
ENV POSTGRES_DB_HOST 'DB_HOST'
ENV POSTGRES_DB_PORT 'DB_PORT'
ENV POSTGRES_DB_USERNAME 'DB_USER'
ENV POSTGRES_DB_PASSWORD 'DB_PASS'

# Copying all the files needed
RUN mkdir -p /wallet-service
WORKDIR /wallet-service
ADD ./ /wallet-service/

# Setting permissions to be executed
RUN chmod +x gunicorn_starter.sh

# Needed to install the postgres library psycopg2 on alphine image
RUN apk add postgresql-dev gcc python3-dev musl-dev

# Installing all python dependences
RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["./gunicorn_starter.sh"]
