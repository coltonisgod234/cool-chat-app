# Testing the Chat Application

This directory contains tests for the chat application. The tests are written using pytest and are designed to test the API endpoints and application functionality.

## Testing Approach

The tests follow these principles:

1. **Test Isolation**: Each test runs in isolation with a fresh application state. The database is cleared between tests to ensure there are no unexpected interactions.

2. **Minimal Dependencies**: Tests interact directly with the application's API rather than mocking dependencies.

3. **Fixtures**: Common setup code is extracted into fixtures to avoid repetition.

## Database Management

For test isolation, we use a `DatabaseCleaner` utility that safely removes test data between runs. This cleaner is specifically designed for testing and should never be used in production code.

The cleaner is implemented in `db_cleaner.py` and:

- Clears messages, channels, guilds, and non-default users between tests
- Preserves the default user (colton) for consistency
- Uses proper session management to avoid SQLAlchemy issues
- Handles entity relationships in the correct order

## Running Tests

To run the tests, use:

```bash
python -m pytest newsrc/tests
```

For more verbose output:

```bash
python -m pytest newsrc/tests -v
```

## Adding New Tests

When adding new tests:

1. Use the existing fixtures wherever possible
2. Ensure your test resets state properly by using the `reset_state` fixture
3. Follow the pattern of creating entities, performing actions, and then asserting results
4. Keep tests focused on testing one specific feature or behavior

## Test Coverage

The tests cover the following functionality:

1. `test_user_authentication` - Tests user creation, login, and logout
2. `test_guild_operations` - Tests guild creation and channel listing
3. `test_channel_operations` - Tests channel creation and listing
4. `test_message_operations` - Tests message creation and retrieval

## Test Structure

The tests use pytest fixtures to set up test environments:

- `client` - Provides a Flask test client
- `reset_state` - Resets the application state between tests
- `test_user` - Creates a test user and returns credentials
- `authenticated_user` - Provides an authenticated user with token
- `test_guild` - Creates a test guild for use in tests
- `test_channel` - Creates a test channel for use in tests

These fixtures help reduce code duplication and ensure tests are isolated from each other.

## Extending Tests

When adding new API endpoints, create corresponding tests that:
1. Test the happy path (successful operation)
2. Test authentication requirements
3. Verify expected responses

Each test function should focus on testing a single piece of functionality. 