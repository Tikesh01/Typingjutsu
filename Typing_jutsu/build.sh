#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python Typing_jutsu/manage.py collectstatic --no-input
python Typing_jutsu/manage.py migrate