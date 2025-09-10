# ERISA-Recovery-Challenge

## Instructions

### load data into database

```bash 
python manage.py makemigrations claims
```

```bash
python manage.py migrate
```

```bash
python manage.py load_claim_data data/claim_list_data.csv data/claim_detail_data.csv --delimiter "|"
```


create user credentials for viewing data. unfortunately no user registration for now.

```bash
python manage.py createsuperuser
```


### run tests

```bash
python manage.py test claims --verbosity=2
```

```bash
coverage run manage.py test claims
```

terminal report

```bash
coverage report -m
```

Detailed HTML Report (Recommended)

```bash
coverage html
```