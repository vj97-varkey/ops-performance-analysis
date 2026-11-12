#!/bin/sh
set -e
pip install -q -r requirements.txt
mkdir -p data output
python generate_data.py
python analysis.py
python -m pytest -q test_project.py
