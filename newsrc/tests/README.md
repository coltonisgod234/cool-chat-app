# API Testing Guide

This directory contains automated tests for the chat app API endpoints.

## Running Tests

To run all tests:

```bash
cd newsrc
python -m pytest tests/ -v
```

To run a specific test file:

```bash
python -m pytest tests/test_endpoints.py -v
```

To run a specific test function:

```bash
python -m pytest tests/test_endpoints.py::test_user_authentication -v
```

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