@echo off
call venv\Scripts\activate.bat
pip install -r requirements.txt
python -m django startproject registration_system . 