import sqlite3

# Replace 'your_database.db' with your database file name
db_path = 'financial_news.db'

# Connect to the database
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Query to list all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in the database:")
for table in tables:
    print(table[0])

# Close the connection
connection.close()
