# shop_parser

Django-based web scraper that parses Apple iPhone products from **brain.com.ua** and stores them in a PostgreSQL database.

## Features

* Parses product pages (name, code, price, specs, images)
* Detects **regular and discounted prices**
* Parses **catalog pages with pagination**
* Handles **product variants** (memory, color)
* Saves data via **Django ORM**
* View products in **Django Admin**

## Tech Stack

* Python
* Django
* BeautifulSoup
* Requests
* PostgreSQL

## Installation

```bash
git clone https://github.com/Olecsiy-Kov/shop_parser.git
cd shop_parser

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

## Run migrations

```bash
python manage.py migrate
```

## Create admin user

```bash
python manage.py createsuperuser
```

## Run parser

Parse single product:

```bash
python manage.py parse_brain_product "<product_url>"
```

Parse full Apple catalog:

```bash
python manage.py parse_all_iphones
```

## Run server

```bash
python manage.py runserver
```

Open Django admin:

```
http://127.0.0.1:8000/admin/
```

## Project Structure

```
shop_parser/
│
├── products/
│   ├── services/
│   │   └── brain_parser.py
│   └── management/commands/
│       ├── parse_brain_product.py
│       └── parse_all_iphones.py
│
├── manage.py
└── requirements.txt
```
