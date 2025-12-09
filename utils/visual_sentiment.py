import cv2
import numpy as np
from deepface import DeepFace
from PIL import Image
import tempfile
import os

class VisualSentimentAnalyzer:
    def __init__(self):
        self.emotion_labels = ['angry', 'disgust', 'fear', 'happy', 
                              'sad', 'surprise', 'neutral']
        
        # Emotion to mood score mapping
        self.emotion_to_score = {
            'angry': 2.0,
            'disgust': 2.5,
            'fear': 3.0,
            'sad': 3.5,
            'neutral': 5.0,
            'surprise': 7.0,
            'happy': 8.5
        }
        
        # Emotion to stress level mapping
        self.emotion_to_stress = {
            'angry': 8.0,
            'disgust': 7.5,
            'fear': 9.0,
            'sad': 7.0,
            'neutral': 5.0,
            'surprise': 4.0,
            'happy': 2.0
        }
    
    def analyze_image(self, image_file):
        """
        Analyze facial expressions in an image
        Returns: dict with emotions, mood score, and stress level
        """
        try:
            # Save image to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                if hasattr(image_file, 'read'):
                    # Handle file upload object
                    image_file.seek(0)
                    tmp_file.write(image_file.read())
                else:
                    # Handle bytes or numpy array
                    tmp_file.write(image_file)
                
                tmp_path = tmp_file.name
            
            # Analyze with DeepFace
            try:
                analysis = DeepFace.analyze(
                    img_path=tmp_path,
                    actions=['emotion', 'age', 'gender'],
                    enforce_detection=False,
                    detector_backend='opencv',
                    silent=True
                )
                
                # Clean up temp file
                os.unlink(tmp_path)
                
                if isinstance(analysis, list):
                    analysis = analysis[0]
                
                # Extract emotions
                emotions = analysis.get('emotion', {})
                
                # Get dominant emotion
                dominant_emotion = analysis.get('dominant_emotion', 'neutral')
                
                # Calculate mood score from emotions
                mood_score = self._calculate_mood_from_emotions(emotions)
                
                # Calculate stress level
                stress_level = self._calculate_stress_from_emotions(emotions)
                
                # Get confidence
                confidence = emotions.get(dominant_emotion, 0) / 100
                
                # Get age and gender
                age = analysis.get('age', 0)
                gender = analysis.get('dominant_gender', 'unknown')
                gender_confidence = analysis.get('gender', {}).get(gender, 0) / 100
                
                return {
                    'success': True,
                    'dominant_emotion': dominant_emotion,
                    'emotions': emotions,
                    'mood_score': round(mood_score, 1),
                    'stress_level': round(stress_level, 1),
                    'confidence': round(confidence, 2),
                    'age': age,
                    'gender': gender,
                    'gender_confidence': round(gender_confidence, 2),
                    'face_detected': True
                }
                
            except Exception as e:
                os.unlink(tmp_path)
                return {
                    'success': False,
                    'error': str(e),
                    'face_detected': False
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'face_detected': False
            }
    
    def analyze_frame(self, frame):
        """
        Analyze a frame (numpy array) from webcam
        """
        try:
            # Convert frame to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                img_pil = Image.fromarray(rgb_frame)
                img_pil.save(tmp_file.name, 'JPEG')
                tmp_path = tmp_file.name
            
            # Analyze
            result = self.analyze_image(tmp_path)
            
            # Draw face rectangle and emotion text on frame
            if result['success'] and result['face_detected']:
                # For simplicity, we'll add text overlay
                # In production, you'd use face detection coordinates
                h, w = frame.shape[:2]
                cv2.putText(frame, f"Mood: {result['mood_score']}/10", 
                          (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Emotion: {result['dominant_emotion']}", 
                          (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Stress: {result['stress_level']}/10", 
                          (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            return frame, result
            
        except Exception as e:
            return frame, {
                'success': False,
                'error': str(e),
                'face_detected': False
            }
    
    def _calculate_mood_from_emotions(self, emotions):
        """Calculate mood score from emotion distribution"""
        if not emotions:
            return 5.0
        
        total_score = 0
        total_weight = 0
        
        for emotion, score in emotions.items():
            if emotion in self.emotion_to_score:
                weight = score / 100  # Convert percentage to decimal
                total_score += self.emotion_to_score[emotion] * weight
                total_weight += weight
        
        if total_weight > 0:
            return total_score / total_weight
        return 5.0
    
    def _calculate_stress_from_emotions(self, emotions):
        """Calculate stress level from emotion distribution"""
        if not emotions:
            return 5.0
        
        total_stress = 0
        total_weight = 0
        
        for emotion, score in emotions.items():
            if emotion in self.emotion_to_stress:
                weight = score / 100
                total_stress += self.emotion_to_stress[emotion] * weight
                total_weight += weight
        
        if total_weight > 0:
            return total_stress / total_weight
        return 5.0
    
    def get_emotion_colors(self):
        """Get colors for each emotion for visualization"""
        return {
            'angry': '#EF476F',     # Red
            'disgust': '#7209B7',   # Purple
            'fear': '#9D0208',      # Dark Red
            'happy': '#06D6A0',     # Green
            'sad': '#4CC9F0',       # Blue
            'surprise': '#FFD166',  # Yellow
            'neutral': '#8D99AE'    # Grey
        }

# Create singleton instance
visual_analyzer = VisualSentimentAnalyzer()