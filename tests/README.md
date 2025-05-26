# Testing the Chat Application

This directory contains tests for the chat application. The tests are written using pytest and are designed to test the API endpoints and application functionality. The test suite supports both SQL (SQLite) and MongoDB database backends.

## Testing Approach

The tests follow these principles:

1. **Test Isolation**: Each test runs in isolation with a fresh application state. The database is cleared between tests to ensure there are no unexpected interactions.

2. **Minimal Dependencies**: Tests interact directly with the application's API rather than mocking dependencies.

3. **Fixtures**: Common setup code is extracted into fixtures to avoid repetition.

4. **Database Agnostic**: Tests are designed to run against both SQL and MongoDB backends.

## Database Management

For test isolation, we use database cleaner utilities that safely remove test data between runs. These cleaners are specifically designed for testing and should never be used in production code.

- `DatabaseCleaner` (in `db_cleaner.py`) - Handles SQLite database cleanup
- `MongoDBCleaner` (in `mongo_db_cleaner.py`) - Handles MongoDB database cleanup

Both cleaners:
- Clear messages, channels, guilds, and non-default users between tests
- Preserve the default user (colton) for consistency
- Handle entity relationships in the correct order

The appropriate cleaner is selected automatically based on the test configuration.

## Database Configuration

The tests use configuration settings from `db_config.py` to determine which database backend to use. You can control this using the `TEST_DB_TYPE` environment variable:

- `TEST_DB_TYPE=sql` (default) - Use SQLite for tests
- `TEST_DB_TYPE=mongo` - Use MongoDB for tests

Additional environment variables for customizing the test database configuration:

- SQLite: `SQL_DB_URL`, `SQL_ECHO`
- MongoDB: `MONGO_URI`, `MONGO_DB_NAME`

## Running Tests

To run the tests, use:

```bash
# Run tests with SQLite (default)
./run_sql_tests.sh

# Run tests with MongoDB 
./run_mongo_tests.sh

# Or use pytest directly
TEST_DB_TYPE=sql python -m pytest tests/ -v
TEST_DB_TYPE=mongo python -m pytest tests/ -v
```

## MongoDB Setup

To run tests with MongoDB, you need to have a MongoDB server running. You can use Docker for a quick setup:

```bash
# Run MongoDB in Docker
docker run --name mongodb -d -p 27017:27017 mongo:latest
```

## Adding New Tests

When adding new tests:

1. Use the existing fixtures wherever possible
2. Ensure your test resets state properly by using the `reset_state` fixture
3. Follow the pattern of creating entities, performing actions, and then asserting results
4. Keep tests focused on testing one specific feature or behavior
5. Ensure tests work with both SQL and MongoDB backends

## Test Coverage

The tests cover the following functionality:

1. `test_user_authentication` - Tests user creation, login, and logout
2. `test_guild_operations` - Tests guild creation and channel listing
3. `test_channel_operations` - Tests channel creation and listing
4. `test_message_operations` - Tests message creation and retrieval

Each test runs against both SQL and MongoDB backends when using the appropriate test script.

## Test Structure

The tests use pytest fixtures to set up test environments:

- `client` - Provides a Flask test client
- `reset_state` - Resets the application state between tests
- `test_user` - Creates a test user and returns credentials
- `authenticated_user` - Provides an authenticated user with token
- `test_guild` - Creates a test guild for use in tests
- `test_channel` - Creates a test channel for use in tests

These fixtures help reduce code duplication and ensure tests are isolated from each other.

## How Database Switching Works

The test setup in `test_endpoints.py` handles database switching as follows:

1. Determine the database type from the `TEST_DB_TYPE` environment variable
2. Create the appropriate database and repositories using `DatabaseFactory`
3. Set up a test database cleaner appropriate for the database type
4. Patch the application services to use the test database
5. Run tests against the configured database

This approach allows the same tests to run against different database backends without code duplication. 