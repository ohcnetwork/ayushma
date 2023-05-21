release: python manage.py migrate
web: gunicorn core.wsgi:application --timeout 180
# worker: REMAP_SIGTERM=SIGQUIT celery -A core.celery_app worker --loglevel=info
# beat: REMAP_SIGTERM=SIGQUIT celery -A core.celery_app beat --loglevel=info
