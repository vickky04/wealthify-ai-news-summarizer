import sqlite3

def reset_articles_table():
    conn = sqlite3.connect('financial_news.db')
    c = conn.cursor()
    # Delete all rows in the articles table
    c.execute('DELETE FROM articles')
    conn.commit()
    conn.close()
    print("Articles table has been reset.")

if __name__ == '__main__':
    reset_articles_table()