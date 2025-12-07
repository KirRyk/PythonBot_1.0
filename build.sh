#!/usr/bin/env bash
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install setuptools==68.0.0
pip install -r requirements.txt