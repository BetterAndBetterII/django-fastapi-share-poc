#!/bin/sh
set -e
cmd="$1"
shift
case "$cmd" in
  django)
    exec python manage.py runserver 0.0.0.0:8000 "$@"
    ;;
  fastapi)
    exec uvicorn fastapi_app.main:app --host 0.0.0.0 --port 8001 "$@"
    ;;
  *)
    exec "$cmd" "$@"
    ;;
esac
