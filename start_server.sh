#!/bin/bash
cd "${0%/*}"

. venv/bin/activate
python main.py
