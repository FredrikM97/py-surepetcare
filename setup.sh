#!/bin/bash
set -e 

if [ -d ".venv" ]; then
  echo "Using existing virtual environment."
else
  python3 -m venv .venv
fi

source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
echo "Don't forget to create your .env file!"