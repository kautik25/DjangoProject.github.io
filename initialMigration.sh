python manage.py makemigrations cities
python manage.py migrate cities
python3 manage.py cities --import=country
python3 manage.py cities --import=region
python3 manage.py cities --import=city
python manage.py makemigrations app
python manage.py migrate app