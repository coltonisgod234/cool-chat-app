import pytest
import os
from flask import Flask

# Import DB factory and configuration
from data.db_factory import DatabaseFactory, DBType
from tests.db_config import get_test_db_type, get_mongo_config, get_sql_config

# Import test utilities
from .db_cleaner import DatabaseCleaner
from .mongo_db_cleaner import MongoDBCleaner

# Initialize database and repositories based on configuration
db_type = get_test_db_type()
db_config = get_mongo_config() if db_type == DBType.MONGO else get_sql_config()
db, user_repo, guild_repo, channel_repo, message_repo = DatabaseFactory.create_database(db_type, **db_config)

# Initialize services for tests
from service.auth_service import AuthService
from service.chat_service import ChatService
auth_service = AuthService(user_repo)
chat_service = ChatService(message_repo, channel_repo, guild_repo, user_repo)

# Initialize test database cleaner
db_cleaner = DatabaseCleaner(db) if db_type == DBType.SQL else MongoDBCleaner(db)

# Patch the environment for the web server
os.environ["DB_TYPE"] = "mongo" if db_type == DBType.MONGO else "sql"
if db_type == DBType.MONGO:
    os.environ["MONGO_DB_NAME"] = db_config["db_name"]

# Import web server *after* setting up the environment and database
from api.web_server import app

# Patch the app's services to use our test services
import api.web_server
api.web_server.auth_service = auth_service
api.web_server.chat_service = chat_service
api.web_server.user_repo = user_repo
api.web_server.guild_repo = guild_repo
api.web_server.channel_repo = channel_repo
api.web_server.message_repo = message_repo
api.web_server.db = db

# Configure test environment
app.config['TESTING'] = True

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def reset_state():
    # Reset in-memory state
    auth_service.users.clear()
    chat_service.guilds.clear()
    chat_service.channels.clear()
    
    # Reset database state using the cleaner
    db_cleaner.reset_database()
    
    # Create default user
    auth_service.initialize_users()

@pytest.fixture
def test_user(client):
    """Create a test user and return username and password"""
    username = "testuser"
    password = "testpass"
    client.post('/api/users/create', json={
        "username": username,
        "password": password
    })
    return username, password

@pytest.fixture
def authenticated_user(client, test_user):
    """Create and authenticate a user, return username and token"""
    username, password = test_user
    resp = client.post('/api/auth/login', json={
        "username": username, 
        "password": password
    })
    token = resp.data.decode()
    return username, token

@pytest.fixture
def test_guild(client, authenticated_user):
    """Create a test guild and return its ID"""
    _, token = authenticated_user
    resp = client.post('/api/guilds/create',
        headers={'Authorization': f'Bearer {token}'}
    )
    return resp.data.decode()

@pytest.fixture
def test_channel(client, authenticated_user, test_guild):
    """Create a test channel in a guild and return its ID"""
    _, token = authenticated_user
    resp = client.post(f'/api/guilds/{test_guild}/new_channel',
        headers={'Authorization': f'Bearer {token}'},
        json={"name": "test-channel"}
    )
    return resp.data.decode()

def test_user_authentication(client):
    """Test user creation, login and logout"""
    username = "cruduser"
    password = "crudpass"
    
    # Reset the auth_service in-memory cache to ensure clean state
    auth_service.users = {}
    
    # Test user creation
    resp = client.post('/api/users/create', json={
        "username": username,
        "password": password
    })
    assert resp.status_code == 200, "User creation should succeed"
    
    # Test login
    resp = client.post('/api/auth/login', json={
        "username": username, 
        "password": password
    })
    assert resp.status_code == 200, "Login with correct password should succeed"
    token = resp.data.decode()
    
    # Test logout
    resp = client.post('/api/auth/logout', 
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200, "Logout should succeed"

def test_guild_operations(client, authenticated_user):
    """Test guild creation and listing channels"""
    _, token = authenticated_user
    
    # Create guild
    resp = client.post('/api/guilds/create',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200, "Guild creation should succeed"
    guild_id = resp.data.decode()
    
    # Check empty channels list
    resp = client.get(f'/api/guilds/{guild_id}/channels_list',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200, "Listing channels should succeed"
    assert resp.json == {"channels": []}, "New guild should have no channels"

def test_channel_operations(client, authenticated_user, test_guild):
    """Test channel creation and listing"""
    _, token = authenticated_user
    guild_id = test_guild
    
    # Create channel
    resp = client.post(f'/api/guilds/{guild_id}/new_channel',
        headers={'Authorization': f'Bearer {token}'},
        json={"name": "general"}
    )
    assert resp.status_code == 200, "Channel creation should succeed"
    
    # List channels
    resp = client.get(f'/api/guilds/{guild_id}/channels_list',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200, "Listing channels should succeed"
    assert len(resp.json["channels"]) == 1, "Guild should have one channel"

def test_message_operations(client, authenticated_user, test_guild, test_channel):
    """Test message creation and retrieval"""
    _, token = authenticated_user
    guild_id = test_guild
    channel_id = test_channel
    
    # Send message
    resp = client.post(f'/api/guilds/{guild_id}/{channel_id}',
        headers={'Authorization': f'Bearer {token}'},
        json={"content": "Hello World"}
    )
    assert resp.status_code == 200, "Sending message should succeed"
    
    # Get messages
    resp = client.get(f'/api/guilds/{guild_id}/{channel_id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200, "Getting messages should succeed"
    assert len(resp.json["messages"]) == 1, "Channel should have one message"

def test_password_change(client, test_user):
    """Test password change functionality"""
    username, old_password = test_user
    new_password = "newpass123"
    
    resp = client.post('/api/auth/login', json={
        "username": username,
        "password": old_password
    })
    assert resp.status_code == 200, "Login with original password should succeed"
    token = resp.data.decode()
    
    resp = client.post('/api/users/change_password',
        headers={'Authorization': f'Bearer {token}'},
        json={
            "old_password": old_password,
            "new_password": new_password
        }
    )
    assert resp.status_code == 200, "Password change should succeed"
    
    # Try login with old password (should fail)
    resp = client.post('/api/auth/login', json={
        "username": username,
        "password": old_password
    })
    assert resp.status_code == 400, "Login with old password should fail"
    
    # Login with new password
    resp = client.post('/api/auth/login', json={
        "username": username,
        "password": new_password
    })
    assert resp.status_code == 200, "Login with new password should succeed" 