# Wealthify – Personalized Financial News Summarizer

## Overview
Wealthify is a full-stack financial news intelligence platform that delivers portfolio-specific news summaries. The system extracts relevant financial articles, filters them based on user portfolio companies, and generates concise summaries using NLP techniques.

The goal is to reduce information overload and provide actionable insights to investors.

---

## Key Features

- Portfolio-based news filtering
- Named Entity Recognition (spaCy) for company extraction
- TF-IDF relevance scoring
- Transformer-based summarization (BART)
- REST API backend using Flask
- SQLite database integration
- Interactive web interface (HTML, CSS, JS)

---

## Tech Stack

**Backend:**
- Python
- Flask
- SQLite

**NLP & ML:**
- spaCy (NER)
- TF-IDF Vectorization
- BART Transformer Model

**Frontend:**
- HTML
- CSS
- JavaScript

---

## System Architecture

1. News data is collected via financial APIs.
2. Articles are processed using Named Entity Recognition.
3. Relevant articles are selected using TF-IDF scoring.
4. Selected content is summarized using BART.
5. Results are stored in a database and served via Flask APIs.
6. Frontend fetches and displays top relevant insights.

---

## How to Run Locally

1. Clone the repository.
2. Navigate into the project directory. 
3. Install dependencies. 
4. Run the application:

---

## Future Improvements

- Deploy using Docker
- Add user authentication
- Integrate real-time streaming APIs
- Improve model performance with fine-tuned transformers

---

## Author

Vickky Kapoor  
Computer Science Undergraduate  



