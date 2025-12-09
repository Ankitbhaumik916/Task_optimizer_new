from utils.sentiment_analyzer import text_analyzer
from utils.visual_sentiment import visual_analyzer
from .sentiment_analyzer import text_analyzer
from .visual_sentiment import visual_analyzer

class FusionEngine:
    def __init__(self):
        self.text_weight = 0.6  # Weight for text analysis
        self.visual_weight = 0.4  # Weight for visual analysis
    
    def analyze_combined(self, text_input=None, image_file=None, manual_mood=None, manual_stress=None):
        """
        Combine text and visual analysis for comprehensive mood assessment
        """
        results = {
            'text_analysis': None,
            'visual_analysis': None,
            'combined_analysis': None,
            'final_mood': 5.0,
            'final_stress': 5.0,
            'confidence': 0.5,
            'recommendations': []
        }
        
        # Analyze text if provided
        if text_input:
            text_result = text_analyzer.analyze_sentiment(text_input)
            results['text_analysis'] = text_result
            
            # Calculate stress from text
            text_stress = text_analyzer.calculate_stress_level(
                text_input, 
                text_result['score']
            )
            
            results['text_analysis']['stress'] = text_stress
        
        # Analyze image if provided
        if image_file:
            visual_result = visual_analyzer.analyze_image(image_file)
            results['visual_analysis'] = visual_result
        
        # Calculate combined scores
        combined_mood = self._fuse_mood_scores(
            results['text_analysis'],
            results['visual_analysis'],
            manual_mood
        )
        
        combined_stress = self._fuse_stress_scores(
            results['text_analysis'],
            results['visual_analysis'],
            manual_stress
        )
        
        # Apply manual overrides if provided
        if manual_mood is not None:
            combined_mood = manual_mood
        
        if manual_stress is not None:
            combined_stress = manual_stress
        
        results['final_mood'] = round(combined_mood, 1)
        results['final_stress'] = round(combined_stress, 1)
        
        # Calculate overall confidence
        results['confidence'] = self._calculate_confidence(
            results['text_analysis'],
            results['visual_analysis']
        )
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(
            results['final_mood'],
            results['final_stress'],
            results['text_analysis'],
            results['visual_analysis']
        )
        
        return results
    
    def _fuse_mood_scores(self, text_analysis, visual_analysis, manual_mood=None):
        """Fuse text and visual mood scores"""
        if manual_mood is not None:
            return manual_mood
        
        text_score = text_analysis['score'] if text_analysis else None
        visual_score = visual_analysis['mood_score'] if visual_analysis and visual_analysis.get('success') else None
        
        if text_score and visual_score:
            # Both available - weighted average
            return (text_score * self.text_weight + 
                   visual_score * self.visual_weight)
        elif text_score:
            return text_score
        elif visual_score:
            return visual_score
        else:
            return 5.0  # Default neutral
    
    def _fuse_stress_scores(self, text_analysis, visual_analysis, manual_stress=None):
        """Fuse text and visual stress scores"""
        if manual_stress is not None:
            return manual_stress
        
        text_stress = text_analysis.get('stress') if text_analysis else None
        visual_stress = visual_analysis.get('stress_level') if visual_analysis and visual_analysis.get('success') else None
        
        if text_stress and visual_stress:
            return (text_stress * self.text_weight + 
                   visual_stress * self.visual_weight)
        elif text_stress:
            return text_stress
        elif visual_stress:
            return visual_stress
        else:
            return 5.0
    
    def _calculate_confidence(self, text_analysis, visual_analysis):
        """Calculate overall confidence score"""
        text_conf = text_analysis['confidence'] if text_analysis else 0
        visual_conf = visual_analysis['confidence'] if visual_analysis and visual_analysis.get('success') else 0
        
        if text_analysis and visual_analysis:
            return (text_conf * self.text_weight + 
                   visual_conf * self.visual_weight)
        elif text_analysis:
            return text_conf
        elif visual_analysis:
            return visual_conf
        else:
            return 0.5
    
    def _generate_recommendations(self, mood, stress, text_analysis, visual_analysis):
        """Generate personalized recommendations"""
        recommendations = []
        
        # Mood-based recommendations
        if mood < 4:
            recommendations.append("Consider taking a short break or doing something you enjoy")
            recommendations.append("Practice deep breathing or mindfulness exercises")
        
        if stress > 7:
            recommendations.append("High stress detected - try the 4-7-8 breathing technique")
            recommendations.append("Consider delegating tasks or discussing workload with team")
        
        # Emotion-specific recommendations
        if visual_analysis and visual_analysis.get('success'):
            emotion = visual_analysis.get('dominant_emotion')
            if emotion == 'angry':
                recommendations.append("Anger detected - try counting to 10 or taking a walk")
            elif emotion == 'sad':
                recommendations.append("Feeling down? Listen to uplifting music or talk to someone")
            elif emotion == 'fear':
                recommendations.append("Anxiety detected - practice grounding techniques")
        
        # Text-based recommendations
        if text_analysis:
            emotions = text_analysis.get('emotions', [])
            if 'tired' in emotions:
                recommendations.append("Fatigue detected - ensure proper rest and hydration")
            if 'productive' in emotions:
                recommendations.append("Great productivity! Maintain momentum with short breaks")
        
        # General wellness tips
        if len(recommendations) < 3:
            recommendations.append("Stay hydrated and take regular screen breaks")
            recommendations.append("Practice good posture and stretch periodically")
        
        return recommendations[:3]  # Return top 3 recommendations

# Create singleton instance
fusion_engine = FusionEngine()