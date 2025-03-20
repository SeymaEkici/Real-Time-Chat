from sqlalchemy import create_engine

# Use your connection string
SQLALCHEMY_DATABASE_URL = "postgresql://chatuser:HappyCat@localhost/chatapp"

try:
    # Try to create an engine and connect
    engine = create_engine(SQLALCHEMY_DATABASE_URL)  # Use the correct variable name
    connection = engine.connect()
    print("Successfully connected to the database!")
    connection.close()
except Exception as e:
    print(f"Error connecting to the database: {e}")
