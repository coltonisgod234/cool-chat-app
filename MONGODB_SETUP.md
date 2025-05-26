# MongoDB Setup Guide

This guide explains how to set up and use MongoDB with the Cool Chat App.

## Prerequisites

- Docker (recommended for easy setup)
- Python 3.10 or higher
- Required Python packages (pymongo, etc.)

## Setting Up MongoDB

### Option 1: Using Docker (Recommended)

The easiest way to set up MongoDB is using Docker:

```bash
# Run MongoDB in Docker
docker run --name mongodb -d -p 27017:27017 mongo:latest

# Verify MongoDB is running
docker ps | grep mongodb
```

### Option 2: Native MongoDB Installation

If you prefer to install MongoDB directly on your system, follow the official MongoDB installation guide for your operating system:
https://www.mongodb.com/docs/manual/installation/

## Configuring the Application

The application can be configured to use MongoDB instead of SQLite by setting environment variables:

```bash
# Basic MongoDB configuration (using defaults)
export DB_TYPE=mongo

# Custom MongoDB configuration
export DB_TYPE=mongo
export MONGO_URI=mongodb://localhost:27017/
export MONGO_DB_NAME=cool_chat_app
```

## Running the Application with MongoDB

Once MongoDB is set up, you can run the application with MongoDB support:

```bash
# Run with MongoDB (using environment variables)
DB_TYPE=mongo python -m api.web_server

# Or set environment variables first
export DB_TYPE=mongo
python -m api.web_server
```

## Running Tests with MongoDB

To run tests with MongoDB:

```bash
# Using the convenience script
./run_mongo_tests.sh

# Or manually
TEST_DB_TYPE=mongo pytest tests/ -v
```

## MongoDB Structure

The application uses the following MongoDB collections:

- `users` - User accounts
- `guilds` - Chat guilds/servers
- `channels` - Chat channels within guilds
- `messages` - Chat messages within channels

## Switching Between SQL and MongoDB

You can easily switch between SQL and MongoDB backends:

```bash
# Use SQLite
unset DB_TYPE
python -m api.web_server

# Use MongoDB
export DB_TYPE=mongo
python -m api.web_server
```

## Troubleshooting

If you encounter issues with MongoDB:

1. Ensure MongoDB is running:
   ```bash
   docker ps | grep mongodb
   ```

2. Check MongoDB logs:
   ```bash
   docker logs mongodb
   ```

3. Connect to MongoDB shell to inspect data:
   ```bash
   docker exec -it mongodb mongosh
   ```

4. Verify connection string and database name:
   ```bash
   echo $MONGO_URI
   echo $MONGO_DB_NAME
   ```

5. Check that pymongo is installed:
   ```bash
   pip show pymongo
   ``` 