import psycopg2

hostname = 'localhost'
database = 'chatapp'
username = 'postgres'
pwd = 'HappyCat'
port_id = 5432
conn = None
cur = None

def connect_db():
    try:
        conn = psycopg2.connect(
            host=hostname,
            dbname=database,
            user=username,
            password=pwd,
            port=port_id
        )
        cur = conn.cursor()
    
        create_script = ''' CREATE TABLE IF NOT EXISTS users(
                                email       varchar PRIMARY KEY,
                                name        varchar(40) NOT NULL,
                                surname     varchar(40) NOT NULL,
                                password    varchar(40) NOT NULL) '''
        cur.execute(create_script)
        conn.commit()
    
    except Exception as error:
        print(f"Error while connecting to the database: {error}")
    
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()