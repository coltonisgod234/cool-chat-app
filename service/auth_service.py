from data.repositories import UserRepository
from . import utils

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        
        # In-memory user cache for faster lookups
        # username -> User
        self.users = {}
        
    def initialize_users(self):
        """Load users from the database into memory cache"""
        # This would typically load users from the database
        # For simplicity, we'll initialize with a default user
        if "colton" not in self.users:
            user = self.user_repo.get_user_by_username("colton")
            if not user:
                default_password_hash = utils.hash_password("defaultpass")
                user = self.user_repo.create_user("colton", default_password_hash)
            self.users["colton"] = user
            
    def login(self, username: str, password: str):
        """Authenticate a user and return a token if successful"""
        if not username or not password:
            utils.log(utils.WARN, f"Login attempt with empty username or password")
            return None
            
        # Get user
        user = self.users.get(username)
        if not user:
            user = self.user_repo.get_user_by_username(username)
            if not user:
                utils.log(utils.WARN, f"Login attempt for non-existent user: {username}")
                return None
            self.users[username] = user
            
        if not user.password_hash:
            utils.log(utils.ERROR, f"User {username} has no password hash set")
            return None
            
        if not utils.verify_password(password, user.password_hash):
            utils.log(utils.WARN, f"Invalid password for user: {username}")
            return None
            
        token = utils.generate_secure_token()
        
        # Always update token through repository to avoid session issues
        success = self.user_repo.update_user_token(user.cid, token)
        if not success:
            utils.log(utils.ERROR, f"Failed to update token for user: {username}")
            return None
            
        user.token = token
        
        utils.log(utils.INFO, f"Successful login for user: {username}")
        return token
        
    def logout(self, username: str):
        """Log out a user by invalidating their token"""
        user = self.users.get(username)
        if not user:
            user = self.user_repo.get_user_by_username(username)
            if not user:
                return False
            self.users[username] = user
            
        success = self.user_repo.update_user_token(user.cid, None)
        if not success:
            return False
            
        user.token = None
        
        utils.log(utils.INFO, f"User logged out: {username}")
        return True
        
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
        if not username or not password:
            utils.log(utils.WARN, f"Attempt to create user with empty username or password")
            return False
            
        # Check if user already exists
        if username in self.users:
            return False
            
        user = self.user_repo.get_user_by_username(username)
        if user:
            # User exists in DB but not in cache
            self.users[username] = user
            return False
            
        # Hash password
        try:
            password_hash = utils.hash_password(password)
        except ValueError as e:
            utils.log(utils.ERROR, f"Password hashing failed: {e}")
            return False
            
        # Create user
        user = self.user_repo.create_user(username, password_hash)
        if not user:
            return False
            
        # Add to cache
        self.users[username] = user
        
        utils.log(utils.INFO, f"Created new user: {username}")
        return True
        
    def change_password(self, username: str, old_password: str, new_password: str):
        """Change a user's password"""
        if not username or not old_password or not new_password:
            return False
            
        user = self.users.get(username)
        if not user:
            user = self.user_repo.get_user_by_username(username)
            if not user:
                return False
            self.users[username] = user
            
        if not user.password_hash or not utils.verify_password(old_password, user.password_hash):
            utils.log(utils.WARN, f"Invalid old password for user: {username}")
            return False
            
        try:
            new_password_hash = utils.hash_password(new_password)
        except ValueError as e:
            utils.log(utils.ERROR, f"Password hashing failed: {e}")
            return False
            
        success = self.user_repo.update_user_password(user.cid, new_password_hash)
        if not success:
            return False
            
        user.password_hash = new_password_hash
        
        # Invalidate token to force re-login
        self.user_repo.update_user_token(user.cid, None)
        user.token = None
        
        utils.log(utils.INFO, f"Password changed for user: {username}")
        return True
        
    def delete_user(self, username: str):
        """Delete a user"""
        user = self.users.get(username)
        if not user:
            user = self.user_repo.get_user_by_username(username)
            if not user:
                return False
                
        success = self.user_repo.delete_user(user.cid)
        if not success:
            return False
            
        if username in self.users:
            del self.users[username]
            
        utils.log(utils.INFO, f"Deleted user: {username}")
        return True
        
    def get_user_by_username(self, username: str):
        """Get a user by username"""
        user = self.users.get(username)
        if not user:
            user = self.user_repo.get_user_by_username(username)
            if user:
                self.users[username] = user
                
        return user
        
    def get_username_by_token(self, token: str):
        """Get a username by token"""
        if not token:
            return None
            
        return self.validate_token(token) 