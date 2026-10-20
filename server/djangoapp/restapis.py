import json
import os
from pathlib import Path
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/")
_sentiment_available = True

DATA_DIR = Path(__file__).resolve().parent.parent / 'database' / 'data'


def _fallback(endpoint):
    dealers = json.loads((DATA_DIR / 'dealerships.json').read_text(encoding='utf-8'))['dealerships']
    reviews = json.loads((DATA_DIR / 'reviews.json').read_text(encoding='utf-8'))['reviews']
    parts = endpoint.strip('/').split('/')
    if parts[0] == 'fetchDealers':
        return dealers if len(parts) == 1 or parts[1] == 'All' else [d for d in dealers if d['state'].lower() == parts[1].lower() or d.get('st', '').lower() == parts[1].lower()]
    if parts[0] == 'fetchDealer' and len(parts) > 1:
        return [d for d in dealers if d['id'] == int(parts[1])]
    if parts[0] == 'fetchReviews':
        return reviews if len(parts) == 1 else [r for r in reviews if r['dealership'] == int(parts[-1])]
    return []


def get_request(endpoint, **kwargs):
    try:
        response = requests.get(f"{backend_url.rstrip('/')}/{endpoint.lstrip('/')}", params=kwargs, timeout=2)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return _fallback(endpoint)

def analyze_review_sentiments(text):
    global _sentiment_available
    try:
        if not _sentiment_available:
            raise requests.RequestException('Sentiment service is offline')
        response = requests.get(f"{sentiment_analyzer_url.rstrip('/')}/analyze/{quote(text, safe='')}", timeout=2)
        response.raise_for_status()
        return response.json().get('sentiment', 'neutral')
    except (requests.RequestException, ValueError):
        _sentiment_available = False
        words = text.lower()
        positive = ('great', 'excellent', 'amazing', 'good', 'love', 'friendly')
        negative = ('bad', 'poor', 'awful', 'terrible', 'hate', 'rude')
        score = sum(word in words for word in positive) - sum(word in words for word in negative)
        return 'positive' if score > 0 else 'negative' if score < 0 else 'neutral'

def post_review(data_dict):
    try:
        response = requests.post(f"{backend_url.rstrip('/')}/insert_review", json=data_dict, timeout=2)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return None
