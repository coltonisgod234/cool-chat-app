# Cool Chat App - Refactored

This is a refactored version of the Cool Chat App with a cleaner architecture and improved organization.

## Project Structure

The project follows a layered architecture pattern with clear separation of concerns:

```
newsrc/
├── api/              # API Layer - HTTP interfaces
│   ├── __init__.py  
│   └── web_server.py # Flask web server and route handlers
├── data/             # Data Layer - Persistence
│   ├── __init__.py
│   ├── database.py   # Database connection management
│   └── repositories.py # Data access objects
├── domain/           # Domain Layer - Business entities
│   ├── __init__.py
│   ├── models.py     # Data models and in-memory models
│   └── permissions.py # Permission system
├── service/          # Service Layer - Business logic
│   ├── __init__.py
│   ├── auth_service.py # Authentication service
│   ├── chat_service.py # Chat management service
│   └── utils.py      # Utility functions
├── tests/            # Test files
│   ├── __init__.py
│   ├── test_endpoints.py # API endpoint tests
│   ├── db_cleaner.py    # Database cleanup utilities
│   └── README.md     # Testing documentation
├── __init__.py       # Package initialization
├── __main__.py       # Application entry point
└── new_web_server.db # SQLite database file
```

## Architecture

- **Domain Layer**: Contains core business models and entities
- **Data Layer**: Handles data persistence with repositories
- **Service Layer**: Implements business logic and orchestrates operations
- **API Layer**: Handles HTTP requests and responses

## Key Components

- **Models**: Define data structures and in-memory representations
- **Repositories**: Handle database operations
- **Services**: Manage business logic and state
- **API Controllers**: Handle HTTP requests and responses

## Running the Application

To run the application, use:

```bash
python -m newsrc
```

## Testing

To run tests, use:

```bash
pytest newsrc/tests -v
``` 