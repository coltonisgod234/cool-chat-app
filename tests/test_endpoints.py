import pytest
from api.web_server import app, auth_service, chat_service, db

# Import test utilities
from .db_cleaner import DatabaseCleaner

# Configure test environment
app.config['TESTING'] = True

# Initialize test database cleaner
db_cleaner = DatabaseCleaner(db)

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