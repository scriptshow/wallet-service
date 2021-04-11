#!/bin/sh
python manage.py migrate
gunicorn --log-level $WALLET_SERVICE_LOG_LEVEL --bind 0.0.0.0:8000 walletservice.wsgi:application
