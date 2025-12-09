import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import streamlit as st

class DashboardVisualizations:
    def __init__(self):
        pass
    
    def create_mood_gauge(self, score, title="Mood Score"):
        """Create a gauge chart for mood score"""
        if score is None:
            score = 5
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': title, 'font': {'size': 20}},
            gauge = {
                'axis': {'range': [1, 10], 'tickwidth': 1},
                'bar': {'color': self._get_mood_color(score)},
                'steps': [
                    {'range': [1, 3], 'color': "#E91111"},  # Red
                    {'range': [3, 5], 'color': "#F8B61D"},  # Yellow
                    {'range': [5, 7], 'color': "#4919C3"},  # Green
                    {'range': [7, 10], 'color': "#003CFF"}  # Blue
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': score
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig
    
    def create_stress_gauge(self, score, title="Stress Level"):
        """Create a gauge chart for stress level"""
        if score is None:
            score = 5
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': title, 'font': {'size': 20}},
            gauge = {
                'axis': {'range': [1, 10], 'tickwidth': 1},
                'bar': {'color': self._get_stress_color(score)},
                'steps': [
                    {'range': [1, 3], 'color': "#06D6A0"},  # Green
                    {'range': [3, 5], 'color': "#FFD166"},  # Yellow
                    {'range': [5, 7], 'color': "#FFA94D"},  # Orange
                    {'range': [7, 10], 'color': "#FF6B6B"}  # Red
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': score
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig
    
    def create_mood_trend_chart(self, mood_data):
        """Create line chart for mood trends"""
        if mood_data.empty:
            # Create placeholder data
            dates = pd.date_range(end=datetime.now(), periods=7).strftime('%Y-%m-%d')
            mood_data = pd.DataFrame({
                'date': dates,
                'avg_mood': [7, 6, 8, 7, 6, 7, 8],
                'avg_stress': [4, 5, 3, 4, 5, 4, 3]
            })
        
        fig = go.Figure()
        
        # Add mood line
        fig.add_trace(go.Scatter(
            x=mood_data['date'],
            y=mood_data['avg_mood'],
            mode='lines+markers',
            name='Mood',
            line=dict(color='#118AB2', width=3),
            marker=dict(size=8)
        ))
        
        # Add stress line
        fig.add_trace(go.Scatter(
            x=mood_data['date'],
            y=mood_data['avg_stress'],
            mode='lines+markers',
            name='Stress',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Mood & Stress Trends",
            xaxis_title="Date",
            yaxis_title="Score (1-10)",
            hovermode='x unified',
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def create_task_completion_chart(self, task_stats):
        """Create donut chart for task completion"""
        labels = ['Completed', 'In Progress', 'To Do']
        values = [
            task_stats.get('completed', 0),
            task_stats.get('in_progress', 0),
            task_stats.get('todo', 0)
        ]
        
        # If all zeros, show placeholder
        if sum(values) == 0:
            labels = ['No Tasks']
            values = [1]
            colors = ['#8D99AE']
        else:
            colors = ['#06D6A0', '#FFD166', '#FF6B6B']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.5,
            marker_colors=colors,
            textinfo='label+value' if sum(values) > 0 else 'label',
            textposition='inside'
        )])
        
        if sum(values) > 0:
            fig.update_layout(
                title="Task Status Distribution",
                height=300,
                showlegend=False,
                annotations=[dict(
                    text=f"{task_stats.get('completion_rate', 0)}%",
                    x=0.5, y=0.5,
                    font_size=20,
                    showarrow=False
                )]
            )
        else:
            fig.update_layout(
                title="Task Status Distribution",
                height=300,
                showlegend=False,
                annotations=[dict(
                    text="No Tasks",
                    x=0.5, y=0.5,
                    font_size=20,
                    showarrow=False
                )]
            )
        
        return fig
    
    def create_team_mood_radar(self, team_mood_data):
        """Create radar chart for team mood comparison"""
        categories = ['Mood', 'Stress', 'Productivity', 'Engagement', 'Energy']
        
        fig = go.Figure()
        
        for member in team_mood_data:
            values = [
                member.get('avg_mood', 5),
                10 - member.get('avg_stress', 5),  # Inverse for radar
                7,  # Placeholder - productivity
                6,  # Placeholder - engagement
                6   # Placeholder - energy
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=member['username']
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[1, 10]
                )
            ),
            showlegend=True,
            height=400,
            title="Team Mood Radar"
        )
        
        return fig
    
    def create_emotion_distribution(self, emotions_list):
        """Create bar chart for emotion distribution"""
        from collections import Counter
        
        # Count emotions
        emotion_counter = Counter()
        for emotions in emotions_list:
            for emotion in emotions:
                emotion_counter[emotion] += 1
        
        if not emotion_counter:
            # Create placeholder
            emotions = ['neutral', 'productive', 'happy']
            counts = [5, 3, 2]
        else:
            emotions = list(emotion_counter.keys())
            counts = list(emotion_counter.values())
        
        # Color map for emotions
        color_map = {
            'happy': '#06D6A0',
            'positive': '#06D6A0',
            'stressed': '#FF6B6B',
            'tired': '#FFD166',
            'anxious': '#FFA94D',
            'frustrated': '#EF476F',
            'productive': '#118AB2',
            'motivated': '#073B4C',
            'neutral': '#8D99AE'
        }
        
        colors = [color_map.get(emotion, '#8D99AE') for emotion in emotions]
        
        fig = go.Figure(data=[go.Bar(
            x=emotions,
            y=counts,
            marker_color=colors,
            text=counts,
            textposition='auto',
        )])
        
        fig.update_layout(
            title="Team Emotion Distribution",
            xaxis_title="Emotions",
            yaxis_title="Count",
            height=300
        )
        
        return fig
    
    def _get_mood_color(self, score):
        """Get color based on mood score"""
        if score >= 8:
            return "#118AB2"  # Blue
        elif score >= 6:
            return "#06D6A0"  # Green
        elif score >= 4:
            return "#FFD166"  # Yellow
        else:
            return "#FF6B6B"  # Red
    
    def _get_stress_color(self, score):
        """Get color based on stress score"""
        if score <= 3:
            return "#06D6A0"  # Green
        elif score <= 5:
            return "#FFD166"  # Yellow
        elif score <= 7:
            return "#FFA94D"  # Orange
        else:
            return "#FF6B6B"  # Red

# Create singleton instance
viz = DashboardVisualizations()