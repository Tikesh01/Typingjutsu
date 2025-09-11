#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

cd Typing_jutsu

python manage.py collectstatic --no-input
python manage.py migrate