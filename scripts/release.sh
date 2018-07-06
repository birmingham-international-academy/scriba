#!/usr/bin/env bash

set -e

echo "Running release tasks..."

python manage.py migrate
python scripts/stanford_parser.py
python -m spacy download en
