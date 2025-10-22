#!/bin/sh
set -e

export PYTHONPATH=$(pwd)

if [ -f .env ]; then
  # shellcheck disable=SC2046
  export $(grep -v '^#' .env | xargs)
fi

uvicorn main:app --host 0.0.0.0 --port 8000 --reload


