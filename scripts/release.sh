#!/usr/bin/env bash

set -e

echo "Running release tasks..."

python -m spacy download en
python scripts/stanford_parser.py
python manage.py migrate
