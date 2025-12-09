import nltk
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
    except:
        print("NLTK download may require additional setup")

class TextSentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        
        # Keywords for stress detection
        self.stress_keywords = [
            'stress', 'stressed', 'overwhelmed', 'busy', 'tired', 'exhausted',
            'anxious', 'worried', 'pressure', 'deadline', 'rush', 'hectic',
            'burnout', 'drained', 'fatigued', 'swamped', 'crazy', 'insane'
        ]
        
        self.positive_keywords = [
            'happy', 'great', 'good', 'excellent', 'awesome', 'fantastic',
            'productive', 'progress', 'achieved', 'completed', 'success',
            'excited', 'motivated', 'energized', 'optimistic', 'positive'
        ]
        
        self.negative_keywords = [
            'bad', 'terrible', 'awful', 'horrible', 'sad', 'depressed',
            'angry', 'frustrated', 'annoyed', 'disappointed', 'failure',
            'stuck', 'blocked', 'problem', 'issue', 'difficult', 'hard'
        ]
    
    def clean_text(self, text):
        """Clean and preprocess text"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)
        
        # Remove special characters and numbers (keep basic punctuation)
        text = re.sub(r'[^a-zA-Z\s.,!?]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def analyze_sentiment(self, text):
        """Analyze sentiment using multiple methods"""
        if not text or len(text.strip()) < 3:
            return {
                'score': 5.0,
                'label': 'neutral',
                'confidence': 0.0,
                'keywords': [],
                'emotions': []
            }
        
        cleaned_text = self.clean_text(text)
        
        # 1. TextBlob Analysis
        try:
            blob = TextBlob(cleaned_text)
            blob_polarity = blob.sentiment.polarity  # -1 to 1
            blob_subjectivity = blob.sentiment.subjectivity  # 0 to 1
        except:
            blob_polarity = 0
            blob_subjectivity = 0
        
        # 2. VADER Analysis
        try:
            vader_scores = self.vader.polarity_scores(cleaned_text)
            vader_compound = vader_scores['compound']  # -1 to 1
        except:
            vader_compound = 0
        
        # 3. Keyword Analysis
        keyword_score = self._keyword_analysis(cleaned_text)
        
        # Combine scores (weighted average)
        # TextBlob: 40%, VADER: 40%, Keywords: 20%
        combined_score = (
            (blob_polarity + 1) * 5 * 0.4 +  # Convert -1:1 to 0:10 scale
            (vader_compound + 1) * 5 * 0.4 +  # Convert -1:1 to 0:10 scale
            keyword_score * 0.2
        )
        
        # Ensure score is between 1-10
        combined_score = max(1, min(10, combined_score))
        
        # Detect emotions
        emotions = self._detect_emotions(cleaned_text)
        
        # Get sentiment label
        label = self._get_sentiment_label(combined_score)
        
        # Calculate confidence
        confidence = (abs(blob_polarity) + abs(vader_compound)) / 2
        
        return {
            'score': round(combined_score, 1),
            'label': label,
            'confidence': round(confidence, 2),
            'keywords': self._extract_keywords(cleaned_text),
            'emotions': emotions,
            'raw_scores': {
                'textblob': blob_polarity,
                'vader': vader_compound,
                'keyword': keyword_score
            }
        }
    
    def _keyword_analysis(self, text):
        """Analyze text for stress/positive/negative keywords"""
        words = text.split()
        
        positive_count = sum(1 for word in words if word in self.positive_keywords)
        negative_count = sum(1 for word in words if word in self.negative_keywords)
        stress_count = sum(1 for word in words if word in self.stress_keywords)
        
        total_keywords = positive_count + negative_count + stress_count
        
        if total_keywords == 0:
            return 5.0  # Neutral score
        
        # Score calculation: positive boosts, negative/stress reduces
        score = 5.0  # Start neutral
        
        if positive_count > 0:
            score += (positive_count / total_keywords) * 3
        
        if negative_count > 0:
            score -= (negative_count / total_keywords) * 3
        
        if stress_count > 0:
            score -= (stress_count / total_keywords) * 2
        
        return max(1, min(10, score))
    
    def _detect_emotions(self, text):
        """Detect emotions from text"""
        emotions = []
        words = text.split()
        
        emotion_map = {
            'happy': ['happy', 'joy', 'excited', 'great', 'good'],
            'stressed': ['stress', 'stressed', 'pressure', 'busy'],
            'tired': ['tired', 'exhausted', 'fatigued', 'sleepy'],
            'anxious': ['anxious', 'worried', 'nervous', 'concerned'],
            'frustrated': ['frustrated', 'annoyed', 'angry', 'mad'],
            'productive': ['productive', 'focused', 'efficient', 'progress'],
            'motivated': ['motivated', 'energized', 'inspired', 'determined'],
            'neutral': ['okay', 'fine', 'alright', 'normal']
        }
        
        for emotion, keywords in emotion_map.items():
            if any(keyword in words for keyword in keywords):
                emotions.append(emotion)
        
        # If no emotions detected, try to infer from sentiment
        if not emotions:
            try:
                blob = TextBlob(text)
                if blob.sentiment.polarity > 0.3:
                    emotions.append('positive')
                elif blob.sentiment.polarity < -0.3:
                    emotions.append('negative')
                else:
                    emotions.append('neutral')
            except:
                emotions.append('neutral')
        
        return list(set(emotions))[:3]  # Return max 3 unique emotions
    
    def _extract_keywords(self, text):
        """Extract important keywords from text"""
        words = text.split()
        
        # Filter out common stop words
        stop_words = {'i', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'should', 'could', 'can', 'may', 'might',
                     'the', 'a', 'an', 'and', 'but', 'or', 'for', 'nor',
                     'on', 'at', 'by', 'to', 'in', 'of', 'with', 'about'}
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Count frequency and get top 5
        from collections import Counter
        word_counts = Counter(keywords)
        top_keywords = [word for word, count in word_counts.most_common(5)]
        
        return top_keywords
    
    def _get_sentiment_label(self, score):
        """Convert score to sentiment label"""
        if score >= 8:
            return "very positive"
        elif score >= 6:
            return "positive"
        elif score >= 4:
            return "neutral"
        elif score >= 2:
            return "negative"
        else:
            return "very negative"
    
    def calculate_stress_level(self, text, mood_score):
        """Calculate stress level from text and mood"""
        if not text:
            return 5
        
        cleaned_text = self.clean_text(text)
        
        # Base stress from mood (inverse relationship)
        stress_from_mood = max(1, 10 - mood_score)
        
        # Stress from keywords
        stress_words = ['stress', 'stressed', 'pressure', 'deadline', 'rush', 
                       'overwhelmed', 'burnout', 'anxious', 'worried']
        
        words = cleaned_text.split()
        stress_word_count = sum(1 for word in words if word in stress_words)
        
        # Adjust stress based on keywords
        if stress_word_count > 0:
            stress_level = min(10, stress_from_mood + (stress_word_count * 0.5))
        else:
            stress_level = stress_from_mood
        
        return round(stress_level, 1)

# Create singleton instance
text_analyzer = TextSentimentAnalyzer()