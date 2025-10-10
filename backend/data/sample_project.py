"""
Sample Python project for testing the Code Assistant AI
"""

class UserManager:
    """Manages user operations"""
    
    def __init__(self):
        self.users = {}
    
    def create_user(self, username: str, email: str) -> dict:
        """Create a new user"""
        if username in self.users:
            raise ValueError("User already exists")
        
        user = {
            'username': username,
            'email': email,
            'created_at': '2025-01-01',
            'active': True
        }
        
        self.users[username] = user
        return user
    
    def get_user(self, username: str) -> dict:
        """Get user by username"""
        if username not in self.users:
            raise ValueError("User not found")
        return self.users[username]
    
    def update_user(self, username: str, **kwargs) -> dict:
        """Update user information"""
        user = self.get_user(username)
        user.update(kwargs)
        return user

def main():
    """Main function"""
    manager = UserManager()
    
    # Create sample users
    manager.create_user("john_doe", "john@example.com")
    manager.create_user("jane_smith", "jane@example.com")
    
    print("Users created successfully!")

if __name__ == "__main__":
    main()
