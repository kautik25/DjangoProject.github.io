#source ./export_configurations.sh
python3 manage.py shell < databaseScript.py
python3 manage.py shell < initSurchargeInfo.py
python3 manage.py shell < initBiller.py
