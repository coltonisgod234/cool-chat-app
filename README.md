# Cool Chat App - Refactored

This is a refactored version of the Cool Chat App with a cleaner architecture and improved organization. The application supports both SQL (SQLite) and MongoDB as database backends.

## Project Structure

The project follows a layered architecture pattern with clear separation of concerns:

```
cool-chat-app/
├── api/              # API Layer - HTTP interfaces
│   ├── __init__.py  
│   └── web_server.py # Flask web server and route handlers
├── data/             # Data Layer - Persistence
│   ├── __init__.py
│   ├── database.py   # SQL database connection management
│   ├── repositories.py # SQL data access objects
│   ├── mongo_database.py # MongoDB connection management
│   ├── mongo_repositories.py # MongoDB data access objects
│   └── db_factory.py # Factory for creating database instances
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
│   ├── db_cleaner.py    # SQL database cleanup utilities
│   ├── mongo_db_cleaner.py # MongoDB cleanup utilities
│   └── db_config.py    # Database configuration for tests
├── run_mongo_tests.sh # Script to run tests with MongoDB
├── run_sql_tests.sh  # Script to run tests with SQLite
├── __init__.py       # Package initialization
├── __main__.py       # Application entry point
└── new_web_server.db # SQLite database file
```

## Architecture

- **Domain Layer**: Contains core business models and entities
- **Data Layer**: Handles data persistence with repositories (SQL and MongoDB)
- **Service Layer**: Implements business logic and orchestrates operations
- **API Layer**: Handles HTTP requests and responses

## Key Components

- **Models**: Define data structures and in-memory representations
- **Repositories**: Handle database operations for both SQL and MongoDB
- **Factory**: Provides a way to switch between SQL and MongoDB backends
- **Services**: Manage business logic and state
- **API Controllers**: Handle HTTP requests and responses

## Database Support

The application supports two database backends:

- **SQLite** (default): A file-based SQL database for simple deployments
- **MongoDB**: A NoSQL document database for more scalable deployments

You can switch between database backends using environment variables:

```bash
# Use SQLite (default)
python -m api.web_server

# Use MongoDB
DB_TYPE=mongo python -m api.web_server

# Use MongoDB with custom connection settings
DB_TYPE=mongo MONGO_URI=mongodb://localhost:27017/ MONGO_DB_NAME=cool_chat_app python -m api.web_server
```

## Running the Application

To run the application, use:

```bash
# With SQLite (default)
python -m api.web_server

# With MongoDB
DB_TYPE=mongo python -m api.web_server
```

## Testing

To run tests, use:

```bash
# Run tests with SQLite
./run_sql_tests.sh

# Run tests with MongoDB
./run_mongo_tests.sh

# Or manually with pytest
TEST_DB_TYPE=sql pytest tests/ -v
TEST_DB_TYPE=mongo pytest tests/ -v
```

## MongoDB Setup

To use MongoDB, you need to have a MongoDB server running. You can use Docker for a quick setup:

```bash
# Run MongoDB in Docker
docker run --name mongodb -d -p 27017:27017 mongo:latest
```

The application will connect to MongoDB at `mongodb://localhost:27017/` by default. You can customize the connection settings using environment variables:

- `MONGO_URI`: MongoDB connection URI (default: `mongodb://localhost:27017/`)
- `MONGO_DB_NAME`: MongoDB database name (default: `cool_chat_app`) 