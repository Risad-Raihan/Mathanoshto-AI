"""
Initialize the 5 fixed users for the application
Run this script once to create the team users
"""
from backend.database.operations import init_database
from backend.database.user_operations import UserDB


# Fixed user credentials
FIXED_USERS = [
    {
        "username": "risad",
        "password": "risad123",  # Change this to your desired password
        "full_name": "Risad",
        "email": "risad@team.com"
    },
    {
        "username": "mazed",
        "password": "mazed123",
        "full_name": "Mazed",
        "email": "mazed@team.com"
    },
    {
        "username": "mrittika",
        "password": "mrittika123",
        "full_name": "Mrittika",
        "email": "mrittika@team.com"
    },
    {
        "username": "nafis",
        "password": "nafis123",
        "full_name": "Nafis",
        "email": "nafis@team.com"
    },
    {
        "username": "rafi",
        "password": "rafi123",
        "full_name": "Rafi",
        "email": "rafi@team.com"
    }
]


def init_users():
    """Initialize all users in the database"""
    print("🚀 Initializing database...")
    init_database()
    
    print("\n👥 Creating fixed users...")
    for user_data in FIXED_USERS:
        try:
            # Check if user already exists
            existing = UserDB.get_user_by_username(user_data["username"])
            if existing:
                print(f"  ⏭️  User '{user_data['username']}' already exists, skipping...")
                continue
            
            # Create new user
            user = UserDB.create_user(
                username=user_data["username"],
                password=user_data["password"],
                full_name=user_data["full_name"],
                email=user_data["email"]
            )
            print(f"  ✅ Created user: {user.username} (ID: {user.id})")
        except Exception as e:
            print(f"  ❌ Failed to create user '{user_data['username']}': {e}")
    
    print("\n✨ User initialization complete!")
    print("\n📝 Login credentials:")
    print("=" * 50)
    for user_data in FIXED_USERS:
        print(f"  Username: {user_data['username']}")
        print(f"  Password: {user_data['password']}")
        print()
    print("=" * 50)
    print("\n⚠️  IMPORTANT: Each user needs to add their own API keys after first login!")


if __name__ == "__main__":
    init_users()

