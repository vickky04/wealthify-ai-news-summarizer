import requests
import re
import sqlite3
from datetime import datetime
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter
from transformers import pipeline

nltk.download('punkt')

NEWS_API_KEY = 'f661a646e66540819ce0a0b3804d0cd4'  # Replace with your NewsAPI key

def fetch_financial_news():
    url = f'https://newsapi.org/v2/everything?q=finance&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        return articles
    else:
        print("Failed to fetch news articles")
        return []

def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    text = re.sub(r'\[[0-9]*\]', '', text)  # Remove references
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    return text.strip()

def score_sentences(text):
    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    word_frequencies = Counter(words)
    sentence_scores = []
    for sentence in sentences:
        score = sum(word_frequencies[word] for word in word_tokenize(sentence))
        sentence_scores.append((score, sentence))
    return sentence_scores

def extractive_summary(text, n=5):
    sentence_scores = score_sentences(text)
    top_sentences = sorted(sentence_scores, reverse=True)[:n]
    summary = " ".join([sentence for score, sentence in top_sentences])
    return summary

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def abstractive_summary(text):
    input_length = len(text.split())
    max_length = min(150, max(30, int(0.5 * input_length)))  # Ensure max_length is at least 30
    min_length = min(30, max(10, int(0.2 * input_length)))  # Ensure min_length is at least 10
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']


def hybrid_summary(text, n=5):
    initial_summary = extractive_summary(text, n)
    final_summary = abstractive_summary(initial_summary)
    return final_summary

def store_article(title, summary, url, published_at):
    try:
        conn = sqlite3.connect('financial_news.db')
        c = conn.cursor()

        # Check for duplicate articles
        c.execute("SELECT id FROM articles WHERE title = ? AND url = ?", (title, url))
        if c.fetchone():
            print(f"Article already exists: {title}")
            return

        c.execute('''
            INSERT INTO articles (title, summary, url, published_at)
            VALUES (?, ?, ?, ?)
        ''', (title, summary, url, published_at))
        conn.commit()
        print(f"Stored article: {title}")
    except sqlite3.Error as e:
        print(f"Error storing article: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    news_articles = fetch_financial_news()
    for article in news_articles:
        title = article.get('title', 'No Title')
        content = preprocess_text(article.get('content', ''))
        summary = hybrid_summary(content)
        url = article.get('url', 'No URL')
        published_at = article.get('publishedAt', 'No Date')
        store_article(title, summary, url, published_at)
        print(f"Stored article: {title}")
        print(summary)







from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import sqlite3
import requests
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key

ALPHA_VANTAGE_API_KEY = 'IBJAG507EFXMV0TB'

def fetch_company_info(stock_symbol):
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={stock_symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    response = requests.get(url)
    return response.json()

def extract_keywords(description):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(description.lower())
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    return filtered_words

def get_keywords_for_portfolio(portfolio):
    keywords_dict = {}
    for stock in portfolio:
        company_info = fetch_company_info(stock)
        if 'Description' in company_info:
            keywords_dict[stock] = extract_keywords(company_info['Description'])
    return keywords_dict

def relevance_score(article_title, keywords):
    score = 0
    article_title = article_title.lower()
    for keyword_list in keywords.values():
        for keyword in keyword_list:
            if keyword in article_title:
                score += 1
    return score

def personalized_summaries(user_id):
    conn = sqlite3.connect('financial_news.db')
    c = conn.cursor()
    c.execute('SELECT * FROM articles')  # Ensure articles are being fetched correctly
    articles = c.fetchall()
    conn.close()

    # Debugging: Check if articles are being fetched correctly
    #print("Fetched Articles:", articles)

    user_portfolio = get_user_portfolio(user_id)
    
    # Debugging: Check portfolio fetched for the user
    #print(f"User Portfolio for ID {user_id}: {user_portfolio}")
    
    keywords = get_keywords_for_portfolio(user_portfolio)
    
    # Debugging: Check if keywords are being extracted properly
    #print(f"Keywords for Portfolio: {keywords}")
    
    ranked_articles = sorted(articles, key=lambda article: relevance_score(article[1], keywords), reverse=True)
    
    # Debugging: Check the ranked articles
    #print(f"Ranked Articles: {ranked_articles}")
    
    return ranked_articles[:10]

def get_user_portfolio(user_id):
    conn = sqlite3.connect('financial_news.db')
    c = conn.cursor()
    c.execute('SELECT portfolio FROM users WHERE id = ?', (user_id,))
    portfolio = c.fetchone()[0].split(',')
    conn.close()
    return portfolio

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    if request.method == 'POST':
        name = request.form['regName']
        email = request.form['regEmail']
        portfolio = request.form['regPortfolio']
        
        conn = sqlite3.connect('financial_news.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (name, email, portfolio) VALUES (?, ?, ?)', (name, email, portfolio))
            conn.commit()
            user_id = c.lastrowid
            message = 'User already exists, returning existing user ID'

        except sqlite3.IntegrityError:
            c.execute('SELECT id FROM users WHERE email = ?', (email,))
            user = c.fetchone()
            if user:
                user_id = user[0]
                message = 'User already exists, returning existing user ID'
            else:
                return jsonify({'message': 'An error occurred during registration.'}), 500
        except Exception as e:
            conn.rollback()
            return jsonify({'message': str(e)}), 500
        finally:
            conn.close()
        
        return redirect(url_for('user_home', user_id=user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        if request.is_json:
            # If the request is JSON (from the fetch API)
            data = request.get_json()
            email = data.get('logEmail')

            conn = sqlite3.connect('financial_news.db')
            c = conn.cursor()
            c.execute('SELECT id FROM users WHERE email = ?', (email,))
            user = c.fetchone()
            conn.close()

            if user:
                # If the user exists, redirect to the user home page
                return redirect(url_for('user_home', user_id=user[0]))
            else:
                # If the user does not exist, return an error message
                return jsonify({"message": "Invalid email"}), 400

        else:
            # Handle traditional form submission (if needed for other cases)
            email = request.form['logEmail']

            conn = sqlite3.connect('financial_news.db')
            c = conn.cursor()
            c.execute('SELECT id FROM users WHERE email = ?', (email,))
            user = c.fetchone()
            conn.close()

            if user:
                return redirect(url_for('user_home', user_id=user[0]))
            else:
                return render_template('login.html', error='Invalid email')



@app.route('/home/<int:user_id>')
def user_home(user_id):
    summaries = personalized_summaries(user_id)
    return render_template('index.html', user_id=user_id, summaries=summaries)

@app.route('/portfolio/<int:user_id>', methods=['GET', 'POST'])
def portfolio(user_id):
    if request.method == 'POST':
        data = request.get_json()
        portfolio = ','.join(data.get('portfolio', []))
        
        conn = sqlite3.connect('financial_news.db')
        c = conn.cursor()
        c.execute('UPDATE users SET portfolio = ? WHERE id = ?', (portfolio, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Portfolio updated successfully'})
    else:
        portfolio = get_user_portfolio(user_id)
        return jsonify(portfolio)

@app.route('/summaries/<int:user_id>', methods=['GET'])
def summaries(user_id):
    summaries = personalized_summaries(user_id)
    return jsonify(summaries)

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    article_id = data['articleId']
    feedback = data['feedback']
    return jsonify({'message': 'Feedback received successfully'})

@app.route('/admin/users', methods=['GET'])
def list_users():
    conn = sqlite3.connect('financial_news.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    conn.close()
    return jsonify(users)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')  # Add a login page template

    if request.method == 'POST':
        data = request.get_json()
        email = data['email']
        password = data['password']
        
        if email == 'rau@1.com' and password == 'raunak':  # Replace with your credentials
            session['admin_logged_in'] = True
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'})


@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = sqlite3.connect('financial_news.db')
    c = conn.cursor()
    try:
        c.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        message = 'User deleted successfully'
    except sqlite3.Error as e:
        message = f"An error occurred: {e}"
    finally:
        conn.close()
    return jsonify({'message': message})

if __name__ == '__main__':
    app.run(debug=True)













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
            summary TEXT,
            url TEXT UNIQUE,
            published_at TEXT
        )
        ''')

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
  
