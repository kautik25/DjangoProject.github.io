# Paybills
# Version : 1.1 

## Installation process

Step - 1 : install virtual environment
```sh
python3 -m pip install virtualenv
```
Step - 2 : create a virtual environment name VENV
```sh
python3 -m virtualenv venv
```
Step - 3 : activate new environment
```sh
source venv/bin/activate
```
Step - 4 : install python modules and packages
```sh
./installPackages
```

## Run migrations and create super user 'admin'

Step - 1 : run migrations for initial setup
```sh
./initialMigration.sh
```
Above migration should be run only once.

Step - 2 : run initial database script to create super user
```sh
./initDatabase.sh
```
In addition to creating super user, above script will also add surcharge information , and biller information.

## Fetch static files
Step - 1 : run script to fetch static files from all the apps
```sh
./collectStatic.sh
```

## Run django backend server

Step - 1 : run server
```sh
./runServer.sh
```
This server will be accessible on http://127.0.0.1:8000/

## Run migrations in case of initial setup has done and models have been modified/added after that

Step - 1 : run migration 
```sh
./migrate.sh
```