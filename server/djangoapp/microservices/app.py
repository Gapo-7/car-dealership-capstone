from flask import Flask
from nltk.sentiment import SentimentIntensityAnalyzer
from pathlib import Path
import nltk

nltk.data.path.insert(0, str(Path(__file__).resolve().parent))
app = Flask("Sentiment Analyzer")

sia = SentimentIntensityAnalyzer()


@app.get('/')
def home():
    return "Welcome to the Sentiment Analyzer. \
    Use /analyze/text to get the sentiment"


@app.get('/analyze/<input_txt>')
def analyze_sentiment(input_txt):

    score = sia.polarity_scores(input_txt)['compound']
    sentiment = 'positive' if score >= 0.05 else 'negative' if score <= -0.05 else 'neutral'
    return {"sentiment": sentiment}


if __name__ == "__main__":
    app.run(debug=True)
