from db_connection import connect_db

# Register a new user
def register_user(email, name, surname, password):
    conn = connect_db()
    if conn is None:
        return "Database connection failed!"

    try:
        cur = conn.cursor()
        
        # Check if user already exists
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()
        
        if existing_user:
            return "User already exists!"
        
        # Insert new user into the database
        insert_query = "INSERT INTO users (email, name, surname, password) VALUES (%s, %s, %s, %s)"
        cur.execute(insert_query, (email, name, surname, password))
        
        conn.commit()
        return "User registered successfully!"
    except Exception as error:
        return f"Error while registering user: {error}"
    finally:
        cur.close()
        conn.close()


# Check user login
def check_user_login(email, password):
    conn = connect_db()
    if conn is None:
        return "Database connection failed!"

    try:
        cur = conn.cursor()
        
        # Check if user exists and password matches
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
        
        if user:
            return "Login successful!"
        else:
            return "Invalid email or password!"
    except Exception as error:
        return f"Error during login: {error}"
    finally:
        cur.close()
        conn.close()
