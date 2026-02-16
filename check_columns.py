import sqlite3
db_path = 'financial_news.db'
table_name = 'articles'  # Replace with the table you want to inspect

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Query to show table schema
cursor.execute(f"PRAGMA table_info({table_name});")
schema = cursor.fetchall()

print(f"Schema of table '{table_name}':")
for column in schema:
    print(f"Column: {column[1]}, Type: {column[2]}")

connection.close()
