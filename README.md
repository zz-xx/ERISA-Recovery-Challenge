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

