#!/bin/sh
python manage.py migrate
gunicorn -w $WALLET_SERVICE_WORKERS --log-level $WALLET_SERVICE_LOG_LEVEL --bind 0.0.0.0:8000 walletservice.wsgi:application
