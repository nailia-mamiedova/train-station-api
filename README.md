# Train Station Api

## Introduction

Welcome to the Train Station API project! This API provides a comprehensive solution 
for managing train stations, routes, trips, and user interactions. 
It is designed to simplify train station management and ticketing operations.

## Running with Docker

Docker must be already installed!

```
git clone https://github.com/nailia-mamiedova/train-station-api
docker-compose build
docker-compose up
```

Use the following command to load prepared data from fixture:

```python manage.py loaddata fixture_data.json```

## Local Setup

Python3 must be already installed!

You also need to install PostgreSQL and create a database.

```
git clone https://github.com/nailia-mamiedova/train-station-api
cd train-station-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
touch .env
python manage.py migrate
python manage.py loaddata fixture_data.json
python manage.py runserver
```

On Windows instead of "touch .env" use command:

```echo > .env```

Fill .env file in according to .env.sample

## Getting access

You can create superuser with :

``` python manage.py createsuperuser ```

or create a default user using api/user/register/

## Features:

- JWT authenticated
- Admin panel: /admin/
- Documentation is located at: </api/doc/swagger/>, </api/doc/redoc/>
- Create trains with train types
- Create routes with source and destination
- Create trips with train, route, crews
- Filter trips by source, destination, arrival time, departure time
- Make Your orders with tickets

### To work with token use:

- get access token and refresh token http://127.0.0.1:8000/api/user/token/
- refresh access token http://127.0.0.1:8000/api/user/token/refresh/
- verify access token http://127.0.0.1:8000/api/user/token/verify/

#### Note: Make sure to send Token in api urls in Headers as follows:

- key: Authorization

- value: Bearer @token
