from textblob import TextBlob
from django.db.models import Count
from .models import VisitorPoints, Feedback
import re
from collections import Counter

def award_points(visitor, workshop, reason, points):
    """
    Awards points to a visitor for a specific reason if not already awarded.
    """
    # Use get_or_create with unique_together to prevent double awarding
    obj, created = VisitorPoints.objects.get_or_create(
        visitor=visitor,
        workshop=workshop,
        reason=reason,
        defaults={'points': points}
    )
    return created

def analyze_sentiment(text):
    """
    Analyzes the sentiment of a given text using TextBlob.
    Returns (label, score)
    """
    if not text:
        return "Neutral", 0.0
    
    analysis = TextBlob(text)
    score = analysis.sentiment.polarity
    
    if score > 0:
        label = "Positive"
    elif score < 0:
        label = "Negative"
    else:
        label = "Neutral"
        
    return label, score

def analyze_and_save_sentiment(feedback):
    """
    Combines all text responses in a feedback and analyzes its overall sentiment.
    """
    text_responses = [
        feedback.question_1_response,
        feedback.question_4_response,
        feedback.question_6_response,
        feedback.question_8_response,
        feedback.question_9_response
    ]
    combined_text = " ".join([r for r in text_responses if r])
    
    if combined_text.strip():
        label, score = analyze_sentiment(combined_text)
        feedback.sentiment = label
        feedback.sentiment_score = score
        feedback.save()

def get_top_keywords(workshop_id, n=10):
    """
    Extracts top keywords from all feedbacks for a specific workshop.
    """
    feedbacks = Feedback.objects.filter(workshop_id=workshop_id)
    text_responses = []
    for f in feedbacks:
        text_responses.extend([
            f.question_1_response,
            f.question_4_response,
            f.question_6_response,
            f.question_8_response,
            f.question_9_response
        ])
    
    combined_text = " ".join([r for r in text_responses if r]).lower()
    # Simple regex to find words (3+ chars)
    words = re.findall(r'\b\w{4,}\b', combined_text)
    
    # Common stop words to exclude (basic set)
    stop_words = {'this', 'that', 'with', 'from', 'very', 'good', 'well', 'great', 'excellent', 'workshop', 'session'}
    filtered_words = [w for w in words if w not in stop_words]
    
    return Counter(filtered_words).most_common(n)
