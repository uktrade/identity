web: python manage.py check --deploy && python manage.py migrate --noinput && python manage.py collectstatic --noinput && ddtrace-run granian --interface wsgi config.wsgi:application --host 0.0.0.0 --port $PORT
peoplefinder: python manage.py check --deploy && python manage.py migrate --noinput && python manage.py collectstatic --noinput && ddtrace-run granian --interface wsgi config.wsgi:application --host 0.0.0.0 --port $PORT
sso-profile: python manage.py check --deploy && python manage.py migrate --noinput && python manage.py collectstatic --noinput && ddtrace-run granian --interface wsgi config.wsgi:application --host 0.0.0.0 --port $PORT
sso-scim: python manage.py check --deploy && python manage.py migrate --noinput && python manage.py collectstatic --noinput && ddtrace-run granian --interface wsgi config.wsgi:application --host 0.0.0.0 --port $PORT
worker: celery -A config worker -l INFO
beat: celery -A config beat -l INFO