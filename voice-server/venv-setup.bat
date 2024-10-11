py -3.10 -m venv %~dp0venv
call %~dp0venv\Scripts\activate.bat
pip install -r %~dp0requirements.txt