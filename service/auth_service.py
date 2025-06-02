from data.repositories import UserRepository
from . import utils
from bcrypt import checkpw, hashpw, gensalt

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        
        # In-memory user cache for faster lookups
        # username -> User
        self.users = {}

    def verify_password(self, password, hash):
        return checkpw(password.encode('utf-8'), hash)
        
    def initialize_users(self):
        """Load users from the database into memory cache"""
        # This would typically load users from the database
        # For simplicity, we'll initialize with a default user
        if "colton" not in self.users:
            # Check if user exists in DB
            user = self.user_repo.get_user_by_username("colton")
            if not user:
                # Create default user if not exists
                user = self.user_repo.create_user("colton", "abc123")
                
            # Add to cache
            self.users["colton"] = user
            
    def login(self, username: str, password: str):
        """Authenticate a user and return a token if successful"""
        # Get user
        user = self.users.get(username)
        if not user:
            user = self.user_repo.get_user_by_username(username)
            if not user:
                return
                
            # Add to cache
            self.users[username] = user
        
        if not self.verify_password(password, user.password_hash):
            return
            
        # In a real app, we'd verify the password
        # For now, just generate a token
        token = utils.generate_id()
        
        # Always update token through repository to avoid session issues
        success = self.user_repo.update_user_token(user.cid, token)
        if not success:
            return None
            
        # Also update in-memory cache
        user.token = token
        
        return token
        
    def logout(self, username: str):
        """Log out a user by invalidating their token"""
        user = self.users.get(username)
        if not user:
            user = self.user_repo.get_user_by_username(username)
            if not user:
                return False
                
            # Add to cache
            self.users[username] = user
            
        # Update token through repository
        success = self.user_repo.update_user_token(user.cid, None)
        if not success:
            return False
            
        # Also update in-memory cache
        user.token = None
        
        return True
    
    def change_password(self, username: str, password: str):
        # Get user
        user = self.users.get(username)
        if not user:
            user = self.user_repo.get_user_by_username(username)
            if not user:
                return
                
            # Add to cache
            self.users[username] = user
        
        user.password_hash = hashpw(password, gensalt())
    def validate_token(self, token: str):
        """Validate a token and return the username if valid"""
        if not token:
            return None
            
        # Check cache first
        for username, user in self.users.items():
            if user.token == token:
                return username
                
        # Check DB
        user = self.user_repo.get_user_by_token(token)
        if user:
            # Update cache
            self.users[user.username] = user
            return user.username
            
        return None
        
    def create_user(self, username: str, password: str):
        """Create a new user"""
        # Check if user already exists
        if username in self.users:
            return False
            
        user = self.user_repo.get_user_by_username(username)
        if user:
            # User exists in DB but not in cache
            self.users[username] = user
            return False
            
        # Create user
        # In a real app, we'd hash the password
        user = self.user_repo.create_user(username, password)
        if not user:
            return False
            
        # Add to cache
        self.users[username] = user
        
        return True
        
    def delete_user(self, username: str):
        """Delete a user"""
        user = self.users.get(username)
        if not user:
            user = self.user_repo.get_user_by_username(username)
            if not user:
                return False
                
        # Delete from DB
        success = self.user_repo.delete_user(user.cid)
        if not success:
            return False
            
        # Remove from cache
        if username in self.users:
            del self.users[username]
            
        return True
        
    def get_user_by_username(self, username: str):
        """Get a user by username"""
        user = self.users.get(username)
        if not user:
            user = self.user_repo.get_user_by_username(username)
            if user:
                # Update cache
                self.users[username] = user
                
        return user
        
    def get_username_by_token(self, token: str):
        """Get a username by token"""
        if not token:
            return None
            
        return self.validate_token(token) 