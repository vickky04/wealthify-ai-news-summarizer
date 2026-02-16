import sqlite3

def create_tables():
    try:
        conn = sqlite3.connect('financial_news.db')
        c = conn.cursor()
        
        # Create articles table
        c.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,  -- Add content column
        summary TEXT,
        url TEXT UNIQUE,
        published_at TEXT
    )
''')
        c.execute("ALTER TABLE articles ADD COLUMN summary TEXT;")
        

        print("Added the 'summary' column to the 'articles' table.")

        # Create users table
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            portfolio TEXT
        )
        ''')
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while creating tables: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    create_tables()