# GalaxyBrainAPI

> A public API bilt with FastAPI that have many interesting facts from different categories.

GalaxyBrainAPI is a lightweight REST API that provides **70+ Facts** across categories like **Space, Science, Technology, History, Animals, Phychology and some wierd facts.**. It includes pagination, searching, filtering, random fact generation, API statistics, automatic database seeding, and interactive Swagger documentation.
Made with **FastAPI**, **SQLAlchemy**, **SQLite**, **Pydantic**, **PEP 8 Style**.

__Fun Fact__: I got idea of this API when i was scrolling and found the galaxy brain meme edit.

## Features

- 70+ Facts
- Multiple categories
- Search Facts by keyword
- Random fact endpoint 
- Pagination SUpport
- Create your own facts
- Statistics endpoint
- Health check endpoint
- FastAPI automatic Swagger & Redoc Docs
- Automatic database seeding

## Demo

**API**

```
https://galaxybrainapi-production.up.railway.app
```

**Swagger Docs**

```
https://galaxybrainapi-production.up.railway.app/docs
```

## Screenshots


## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend |
| FastAPI | REST API Framework |
| SQLAlchemy | ORM |
| SQLite | Database |
| Pydantic | Validation |
| Uvicorn | ASGI Server |

## Project Structure 

## 📂 Project Structure

```text
GalaxyBrainAPI/
│
├── app/
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── routes/
│       ├── facts.py
│       └── stats.py
│
├── data/
│   └── seed_data.py
│
├── tests/
│   └── test_api.py
│
├── requirements.txt
├── galaxy_brain.db
└── README.md
``` 


