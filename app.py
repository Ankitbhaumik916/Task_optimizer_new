import streamlit as st
from auth.authentication import authenticator
from database.models import db
from database.operations import db_ops
from utils.sentiment_analyzer import text_analyzer
from utils.visualizations import viz
import time
# Add this with your other imports at the top of app.py
import plotly.express as px
from datetime import datetime, timedelta
# Add these imports
from utils.fusion_engine import fusion_engine
from utils.visual_sentiment import visual_analyzer

# Page configuration
st.set_page_config(
    page_title="Team Optimizer AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .stButton > button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .task-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1E88E5;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .urgent-task {
        border-left-color: #FF6B6B !important;
        background-color: #FFF5F5;
    }
    .high-priority {
        border-left-color: #FFA94D;
    }
    .completed-task {
        border-left-color: #06D6A0;
        opacity: 0.7;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Show login page if not authenticated
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_main_app()

def show_login_page():
    """Display the login/signup page"""
    st.markdown('<h1 class="main-header">🧠 Team Optimizer AI</h1>', unsafe_allow_html=True)
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    authenticator.show_login_page()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col2:
        st.caption("AI-Powered Team Management")

def show_main_app():
    """Display the main application after login"""
    
    # Sidebar navigation
    with st.sidebar:
        st.title(f"👋 Welcome, {st.session_state.user['username']}")
        st.markdown("---")
        
        # Navigation menu
        st.subheader("Navigation")
        page = st.radio(
            "Go to:",
            ["Dashboard", "Mood Tracker", "Task Manager", "Team Management", "Analytics", "Settings"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Quick stats from database
        user_id = st.session_state.user['id']
        team_id = st.session_state.user['team_id']
        
        if team_id:
            team_stats = db_ops.get_team_stats(team_id)
            task_stats = db_ops.get_task_stats(user_id)
            today_mood = db_ops.get_today_mood_stats(user_id)
            
            st.subheader("Quick Stats")
            col1, col2 = st.columns(2)
            with col1:
                mood_val = today_mood['avg_mood'] if today_mood['avg_mood'] else team_stats['avg_mood']
                st.metric("Team Mood", f"{mood_val:.1f}")
            with col2:
                st.metric("Tasks Done", f"{task_stats['completed']}/{task_stats['total']}")
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    # Main content area based on selection
    if page == "Dashboard":
        show_dashboard()
    elif page == "Mood Tracker":
        show_mood_tracker()
    elif page == "Task Manager":
        show_task_manager()
    elif page == "Team Management":
        show_team_management()
    elif page == "Analytics":
        show_analytics()
    elif page == "Settings":
        show_settings()

def show_dashboard():
    """Dashboard with real data"""
    st.title("📊 Dashboard")
    
    user_id = st.session_state.user['id']
    team_id = st.session_state.user['team_id']
    
    if not team_id:
        st.warning("You are not part of a team yet. Please ask your admin to add you.")
        return
    
    # Get data from database
    team_stats = db_ops.get_team_stats(team_id)
    task_stats = db_ops.get_task_stats(user_id)
    today_mood = db_ops.get_today_mood_stats(user_id)
    team_mood_summary = db_ops.get_team_mood_summary(team_id)
    
    # Row 1: Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        mood_val = today_mood['avg_mood'] if today_mood['avg_mood'] else team_stats['avg_mood']
        st.metric("Average Mood", f"{mood_val}/10", 
                 f"{'+' if mood_val > 7 else ''}{mood_val - 7:.1f}" if mood_val else "N/A")
    
    with col2:
        st.metric("Task Completion", f"{task_stats['completion_rate']}%", 
                 f"{'+' if task_stats['completion_rate'] > 50 else ''}{task_stats['completion_rate'] - 50:.1f}%")
    
    with col3:
        stress_val = today_mood['avg_stress'] if today_mood['avg_stress'] else team_stats['avg_stress']
        st.metric("Stress Level", f"{stress_val}/10")
    
    with col4:
        urgent_tasks = task_stats.get('urgent', 0)
        st.metric("Urgent Tasks", urgent_tasks, 
                 "⚠️ High" if urgent_tasks > 3 else "✓ OK")
    
    st.markdown("---")
    
    # Row 2: Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Mood Gauge
        fig = viz.create_mood_gauge(mood_val, "Your Mood Today")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Task Completion Chart
        fig = viz.create_task_completion_chart(task_stats)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 3: Team Mood and Active Tasks
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Team Mood Today")
        
        if team_mood_summary:
            for member in team_mood_summary:
                if member['avg_mood'] > 0:
                    cols = st.columns([3, 2, 2])
                    with cols[0]:
                        st.write(f"👤 {member['username']}")
                    with cols[1]:
                        mood_score = member['avg_mood']
                        color = viz._get_mood_color(mood_score)
                        st.markdown(f"<span style='color:{color}; font-weight:bold;'>{mood_score:.1f}/10</span>", 
                                  unsafe_allow_html=True)
                    with cols[2]:
                        stress_score = member['avg_stress']
                        color = viz._get_stress_color(stress_score)
                        st.markdown(f"<span style='color:{color};'>Stress: {stress_score:.1f}</span>", 
                                  unsafe_allow_html=True)
        else:
            st.info("No mood entries from team members today")
    
    with col2:
        st.subheader("Active Tasks")
        
        user_tasks = db_ops.get_user_tasks(user_id)
        
        if user_tasks:
            for task in user_tasks[:5]:  # Show only 5 tasks
                task_class = "task-card"
                if task['priority'] == 'urgent':
                    task_class += " urgent-task"
                elif task['priority'] == 'high':
                    task_class += " high-priority"
                elif task['status'] == 'completed':
                    task_class += " completed-task"
                
                st.markdown(f'<div class="{task_class}">', unsafe_allow_html=True)
                
                cols = st.columns([4, 1])
                with cols[0]:
                    st.write(f"**{task['title']}**")
                    if task['description']:
                        st.caption(task['description'][:50] + "..." if len(task['description']) > 50 else task['description'])
                with cols[1]:
                    status = task['status'].replace('_', ' ').title()
                    st.caption(f"📌 {status}")
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No tasks assigned to you")
            
            # Quick add task
            with st.expander("➕ Add Quick Task"):
                quick_title = st.text_input("Task title", key="quick_task")
                if st.button("Add Task"):
                    if quick_title:
                        db_ops.create_task(quick_title, "Quick task from dashboard", user_id)
                        st.success("Task added!")
                        st.rerun()
    
    # Row 4: Mood Trends
    st.markdown("---")
    st.subheader("Your Mood Trends")
    
    mood_history = db_ops.get_user_mood_history(user_id, days=7)
    
    if not mood_history.empty:
        fig = viz.create_mood_trend_chart(mood_history)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No mood history yet. Start tracking your mood!")

def show_mood_tracker():
    """Enhanced Mood Tracker with Computer Vision"""
    st.title("🎭 Mood Tracker")
    
    user_id = st.session_state.user['id']
    
    # Check privacy settings for visual tracking
    allow_visual = st.session_state.get('allow_visual_tracking', True)
    
    # Tabs for different tracking methods
    if allow_visual:
        tab1, tab2, tab3, tab4 = st.tabs(["Text + Visual", "Text Only", "Visual Only", "History"])
    else:
        tab1, tab2, tab3 = st.tabs(["Text Analysis", "Quick Check", "History"])
    
    if allow_visual:
        with tab1:
            show_combined_analysis(user_id)
        
        with tab2:
            show_text_analysis(user_id)
        
        with tab3:
            show_visual_analysis(user_id)
        
        with tab4:
            show_mood_history(user_id)
    else:
        with tab1:
            show_text_analysis(user_id)
        
        with tab2:
            show_quick_check(user_id)
        
        with tab3:
            show_mood_history(user_id)

def show_combined_analysis(user_id):
    """Combined text and visual analysis"""
    st.subheader("📝 Text + 📸 Visual Analysis")
    st.write("Get the most accurate mood analysis by combining text description with facial expression analysis.")
    
    # Text input
    mood_text = st.text_area(
        "How are you feeling today?",
        placeholder="Describe your current mood, workload, or anything affecting your day...",
        height=120,
        key="combined_text"
    )
    
    # Manual overrides
    col1, col2 = st.columns(2)
    with col1:
        manual_mood = st.slider("Self-reported mood (1-10)", 1, 10, 7, 
                               key="combined_mood", help="Your subjective mood rating")
    with col2:
        manual_stress = st.slider("Stress level (1-10)", 1, 10, 5, 
                                 key="combined_stress", help="Your perceived stress level")
    
    # Visual analysis section
    st.subheader("Facial Expression Analysis")
    
    visual_method = st.radio(
        "Choose analysis method:",
        ["Take a photo", "Upload existing photo", "Skip visual analysis"],
        horizontal=True
    )
    
    image_file = None
    visual_result = None
    
    if visual_method == "Take a photo":
        picture = st.camera_input("Smile for the camera! 😊", key="camera_combined")
        if picture:
            image_file = picture
            with st.spinner("Analyzing facial expressions..."):
                from utils.visual_sentiment import visual_analyzer
                visual_result = visual_analyzer.analyze_image(image_file)
    
    elif visual_method == "Upload existing photo":
        uploaded_file = st.file_uploader("Upload a selfie", 
                                       type=['jpg', 'jpeg', 'png'],
                                       key="upload_combined")
        if uploaded_file:
            image_file = uploaded_file
            with st.spinner("Analyzing facial expressions..."):
                from utils.visual_sentiment import visual_analyzer
                visual_result = visual_analyzer.analyze_image(image_file)
    
    # Display visual analysis results
    if visual_result and visual_result.get('success'):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            mood_score = visual_result['mood_score']
            color = viz._get_mood_color(mood_score)
            st.metric("Visual Mood", f"{mood_score:.1f}/10")
        
        with col2:
            stress_level = visual_result['stress_level']
            stress_color = viz._get_stress_color(stress_level)
            st.metric("Visual Stress", f"{stress_level:.1f}/10")
        
        with col3:
            emotion = visual_result['dominant_emotion'].title()
            st.metric("Dominant Emotion", emotion)
        
        # Show emotion distribution
        if visual_result.get('emotions'):
            show_emotion_chart(visual_result['emotions'])
    
    elif visual_method != "Skip visual analysis" and visual_result:
        if not visual_result.get('face_detected'):
            st.warning("No face detected in the image. Please try again with a clearer photo.")
        else:
            st.error(f"Analysis failed: {visual_result.get('error', 'Unknown error')}")
    
    # Analyze and save button
    if st.button("🚀 Analyze & Save Combined Mood", type="primary", use_container_width=True):
        if not mood_text.strip() and not image_file:
            st.error("Please provide either text description or photo for analysis")
        else:
            with st.spinner("Analyzing combined mood..."):
                from utils.fusion_engine import fusion_engine
                
                # Perform combined analysis
                combined_result = fusion_engine.analyze_combined(
                    text_input=mood_text if mood_text.strip() else None,
                    image_file=image_file,
                    manual_mood=manual_mood if manual_mood != 7 else None,
                    manual_stress=manual_stress if manual_stress != 5 else None
                )
                
                # Save to database
                entry_id = db_ops.create_mood_entry(
                    user_id=user_id,
                    text_entry=mood_text if mood_text.strip() else "Visual analysis only",
                    text_sentiment=combined_result['final_mood'],
                    visual_sentiment=visual_result['mood_score'] if visual_result and visual_result.get('success') else None,
                    stress_level=combined_result['final_stress']
                )
                
                # Display results
                show_combined_results(combined_result, entry_id)

def show_text_analysis(user_id):
    """Text-only mood analysis"""
    st.subheader("📝 Text-based Mood Analysis")
    
    mood_text = st.text_area(
        "Describe your feelings:",
        placeholder="How has your day been? What's on your mind?",
        height=150,
        key="text_only"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        manual_mood = st.slider("Your mood rating", 1, 10, 7, key="text_mood")
    with col2:
        manual_stress = st.slider("Your stress level", 1, 10, 5, key="text_stress")
    
    if st.button("Analyze Text Mood", type="primary", use_container_width=True):
        if not mood_text.strip():
            st.error("Please describe your feelings")
        else:
            with st.spinner("Analyzing text sentiment..."):
                # Analyze text
                text_result = text_analyzer.analyze_sentiment(mood_text)
                
                # Calculate stress
                calculated_stress = text_analyzer.calculate_stress_level(
                    mood_text, 
                    text_result['score']
                )
                
                # Use manual or calculated values
                final_mood = manual_mood if manual_mood != 7 else text_result['score']
                final_stress = manual_stress if manual_stress != 5 else calculated_stress
                
                # Save to database
                entry_id = db_ops.create_mood_entry(
                    user_id=user_id,
                    text_entry=mood_text,
                    text_sentiment=final_mood,
                    stress_level=final_stress
                )
                
                # Show results
                st.success("Mood entry saved!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Mood Score", f"{final_mood:.1f}/10")
                with col2:
                    st.metric("Stress Level", f"{final_stress:.1f}/10")
                with col3:
                    st.metric("Confidence", f"{text_result['confidence']*100:.0f}%")
                
                # Show emotions
                if text_result['emotions']:
                    st.write("**Detected emotions:**")
                    for emotion in text_result['emotions']:
                        st.write(f"• {emotion.title()}")

def show_visual_analysis(user_id):
    """Visual-only mood analysis"""
    st.subheader("📸 Visual Mood Analysis")
    st.write("Analyze your mood through facial expressions")
    
    tab1, tab2 = st.tabs(["Take Photo", "Upload Photo"])
    
    with tab1:
        picture = st.camera_input("Look at the camera naturally", key="camera_visual")
        if picture:
            analyze_and_save_visual(user_id, picture)
    
    with tab2:
        uploaded_file = st.file_uploader("Choose a selfie", 
                                       type=['jpg', 'jpeg', 'png'],
                                       key="upload_visual")
        if uploaded_file:
            analyze_and_save_visual(user_id, uploaded_file)

def analyze_and_save_visual(user_id, image_file):
    """Helper function to analyze and save visual mood"""
    with st.spinner("Analyzing facial expressions..."):
        from utils.visual_sentiment import visual_analyzer
        result = visual_analyzer.analyze_image(image_file)
        
        if result.get('success'):
            # Save to database
            entry_id = db_ops.create_mood_entry(
                user_id=user_id,
                text_entry="Visual analysis entry",
                visual_sentiment=result['mood_score'],
                stress_level=result['stress_level']
            )
            
            # Display results
            st.success("Visual mood analysis saved!")
            
            # Show image
            st.image(image_file, caption="Analyzed Image", use_column_width=True)
            
            # Show metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mood Score", f"{result['mood_score']:.1f}/10")
            with col2:
                st.metric("Stress Level", f"{result['stress_level']:.1f}/10")
            with col3:
                st.metric("Dominant Emotion", result['dominant_emotion'].title())
            
            # Show emotion chart
            show_emotion_chart(result['emotions'])
            
            # Show additional info
            with st.expander("Detailed Analysis"):
                st.write(f"**Age:** {result.get('age', 'N/A')}")
                st.write(f"**Gender:** {result.get('gender', 'N/A')} "
                        f"(confidence: {result.get('gender_confidence', 0)*100:.0f}%)")
                st.write(f"**Analysis Confidence:** {result.get('confidence', 0)*100:.0f}%")
        
        else:
            if not result.get('face_detected'):
                st.error("❌ No face detected. Please ensure your face is clearly visible.")
            else:
                st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")

def show_quick_check(user_id):
    """Quick mood check without detailed analysis"""
    st.subheader("⚡ Quick Mood Check")
    st.write("Quickly log your mood without detailed analysis")
    
    quick_moods = [
        ("😊 Excellent", 9, 2, "#06D6A0"),
        ("🙂 Good", 7, 3, "#4CC9F0"),
        ("😐 Okay", 5, 5, "#FFD166"),
        ("😕 Stressed", 3, 8, "#F4A261"),
        ("😟 Difficult", 2, 9, "#EF476F")
    ]
    
    cols = st.columns(5)
    for idx, (label, mood, stress, color) in enumerate(quick_moods):
        with cols[idx]:
            if st.button(label, use_container_width=True, 
                        help=f"Mood: {mood}/10, Stress: {stress}/10"):
                db_ops.create_mood_entry(
                    user_id=user_id,
                    text_entry=f"Quick check: {label}",
                    text_sentiment=mood,
                    stress_level=stress
                )
                st.success(f"{label} mood saved!")
                st.rerun()
    
    # Custom quick entry
    with st.expander("Custom Quick Entry"):
        col1, col2 = st.columns(2)
        with col1:
            custom_mood = st.slider("Mood", 1, 10, 5, key="quick_mood")
        with col2:
            custom_stress = st.slider("Stress", 1, 10, 5, key="quick_stress")
        
        note = st.text_input("Quick note (optional)", placeholder="Brief note...")
        
        if st.button("Save Quick Entry"):
            db_ops.create_mood_entry(
                user_id=user_id,
                text_entry=note if note else "Quick mood entry",
                text_sentiment=custom_mood,
                stress_level=custom_stress
            )
            st.success("Quick entry saved!")
            st.rerun()

def show_mood_history(user_id):
    """Display mood history"""
    st.subheader("📊 Mood History")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        days = st.selectbox("Time period", [7, 14, 30, 90], index=0)
    with col2:
        show_chart = st.checkbox("Show chart", value=True)
    with col3:
        if st.button("Refresh", use_container_width=True):
            st.rerun()
    
    # Get history
    history = db_ops.get_user_mood_history(user_id, days)
    
    if not history.empty:
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_mood = history['avg_mood'].mean()
            st.metric("Average Mood", f"{avg_mood:.1f}/10")
        with col2:
            avg_stress = history['avg_stress'].mean()
            st.metric("Average Stress", f"{avg_stress:.1f}/10")
        with col3:
            best_day = history['avg_mood'].max()
            st.metric("Best Day", f"{best_day:.1f}/10")
        with col4:
            consistency = history['avg_mood'].std()
            st.metric("Consistency", f"{consistency:.2f} std")
        
        # Show chart
        if show_chart:
            fig = viz.create_mood_trend_chart(history)
            st.plotly_chart(fig, use_container_width=True)
        
        # Show table
        st.subheader("Daily Summary")
        st.dataframe(
            history,
            column_config={
                "date": st.column_config.DateColumn("Date", format="MMM D, YYYY"),
                "avg_mood": st.column_config.NumberColumn(
                    "Mood",
                    format="%.1f",
                    help="Average mood score"
                ),
                "avg_stress": st.column_config.NumberColumn(
                    "Stress",
                    format="%.1f",
                    help="Average stress level"
                ),
                "entries": st.column_config.NumberColumn(
                    "Entries",
                    help="Number of mood entries"
                )
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No mood history found. Start tracking your mood!")

def show_combined_results(combined_result, entry_id):
    """Display combined analysis results"""
    st.success(f"✅ Mood entry #{entry_id} saved successfully!")
    
    # Show final scores
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Final Mood Score", f"{combined_result['final_mood']}/10")
    with col2:
        st.metric("Final Stress Level", f"{combined_result['final_stress']}/10")
    with col3:
        st.metric("Analysis Confidence", f"{combined_result['confidence']*100:.0f}%")
    
    # Show breakdown
    with st.expander("📊 Analysis Breakdown"):
        if combined_result['text_analysis']:
            st.subheader("Text Analysis")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Score:** {combined_result['text_analysis']['score']}/10")
                st.write(f"**Label:** {combined_result['text_analysis']['label']}")
            with col2:
                st.write(f"**Emotions:** {', '.join(combined_result['text_analysis']['emotions'])}")
                if combined_result['text_analysis'].get('stress'):
                    st.write(f"**Stress:** {combined_result['text_analysis']['stress']}/10")
        
        if combined_result['visual_analysis'] and combined_result['visual_analysis'].get('success'):
            st.subheader("Visual Analysis")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Mood:** {combined_result['visual_analysis']['mood_score']}/10")
                st.write(f"**Stress:** {combined_result['visual_analysis']['stress_level']}/10")
            with col2:
                st.write(f"**Dominant Emotion:** {combined_result['visual_analysis']['dominant_emotion']}")
                st.write(f"**Confidence:** {combined_result['visual_analysis']['confidence']*100:.0f}%")
    
    # Show recommendations
    if combined_result['recommendations']:
        st.subheader("💡 Personalized Recommendations")
        for i, rec in enumerate(combined_result['recommendations'], 1):
            st.write(f"{i}. {rec}")

def show_emotion_chart(emotions):
    """Display emotion distribution chart"""
    if not emotions:
        return
    
    import plotly.graph_objects as go
    
    # Get colors
    from utils.visual_sentiment import visual_analyzer
    colors = visual_analyzer.get_emotion_colors()
    
    # Prepare data
    emotion_names = list(emotions.keys())
    emotion_values = list(emotions.values())
    emotion_colors = [colors.get(emotion, '#8D99AE') for emotion in emotion_names]
    
    # Create chart
    fig = go.Figure(data=[go.Bar(
        x=emotion_names,
        y=emotion_values,
        marker_color=emotion_colors,
        text=[f"{v:.1f}%" for v in emotion_values],
        textposition='auto',
    )])
    
    fig.update_layout(
        title="Emotion Distribution",
        xaxis_title="Emotions",
        yaxis_title="Percentage (%)",
        height=300,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_task_manager():
    """Complete Task Manager with CRUD Operations"""
    st.title("📋 Task Manager")
    
    user_id = st.session_state.user['id']
    team_id = st.session_state.user['team_id']
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["My Tasks", "Team Tasks", "Create Task"])
    
    with tab1:
        st.subheader("Your Tasks")
        
        # Status filter
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "todo", "in_progress", "completed"],
            key="my_tasks_filter"
        )
        
        # Get user tasks
        tasks = db_ops.get_user_tasks(
            user_id, 
            status_filter if status_filter != "All" else None
        )
        
        if tasks:
            for task in tasks:
                # Determine card class
                card_class = "task-card"
                if task['priority'] == 'urgent':
                    card_class += " urgent-task"
                elif task['priority'] == 'high':
                    card_class += " high-priority"
                elif task['status'] == 'completed':
                    card_class += " completed-task"
                
                st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                
                # Task header
                cols = st.columns([4, 1])
                with cols[0]:
                    st.write(f"**{task['title']}**")
                with cols[1]:
                    # Status badge
                    status_colors = {
                        'todo': '#FF6B6B',
                        'in_progress': '#FFD166',
                        'completed': '#06D6A0'
                    }
                    status_color = status_colors.get(task['status'], '#8D99AE')
                    status_text = task['status'].replace('_', ' ').title()
                    st.markdown(f'<span style="color:{status_color}; font-weight:bold;">{status_text}</span>', 
                              unsafe_allow_html=True)
                
                # Task details
                if task['description']:
                    st.write(task['description'])
                
                # Task metadata
                meta_cols = st.columns(4)
                with meta_cols[0]:
                    # Priority badge
                    priority_colors = {
                        'urgent': '#FF6B6B',
                        'high': '#FFA94D',
                        'medium': '#FFD166',
                        'low': '#06D6A0'
                    }
                    priority_color = priority_colors.get(task['priority'], '#8D99AE')
                    st.markdown(f'📌 <span style="color:{priority_color};">{task["priority"].title()}</span>', 
                              unsafe_allow_html=True)
                
                with meta_cols[1]:
                    if task['deadline']:
                        deadline = task['deadline']
                        if isinstance(deadline, str):
                            deadline = datetime.strptime(deadline, '%Y-%m-%d').date()
                        elif isinstance(deadline, datetime):
                            deadline = deadline.date()
                        
                        days_left = (deadline - datetime.now().date()).days
                        if days_left < 0:
                            st.markdown(f'📅 <span style="color:#FF6B6B;">Overdue by {-days_left} days</span>', 
                                      unsafe_allow_html=True)
                        elif days_left == 0:
                            st.markdown(f'📅 <span style="color:#FFA94D;">Due today</span>', 
                                      unsafe_allow_html=True)
                        elif days_left <= 3:
                            st.markdown(f'📅 <span style="color:#FFD166;">Due in {days_left} days</span>', 
                                      unsafe_allow_html=True)
                        else:
                            st.markdown(f'📅 Due {deadline.strftime("%b %d")}', unsafe_allow_html=True)
                
                # Action buttons
                action_cols = st.columns(3)
                with action_cols[0]:
                    if task['status'] != 'completed':
                        if st.button("✅ Complete", key=f"complete_{task['id']}"):
                            db_ops.update_task_status(task['id'], 'completed')
                            st.success("Task marked as completed!")
                            time.sleep(1)
                            st.rerun()
                
                with action_cols[1]:
                    if task['status'] != 'in_progress':
                        if st.button("▶️ Start", key=f"start_{task['id']}"):
                            db_ops.update_task_status(task['id'], 'in_progress')
                            st.success("Task marked as in progress!")
                            time.sleep(1)
                            st.rerun()
                
                with action_cols[2]:
                    if st.button("🗑️ Delete", key=f"delete_{task['id']}"):
                        db_ops.delete_task(task['id'])
                        st.success("Task deleted!")
                        time.sleep(1)
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No tasks found. Create your first task!")
    
    with tab2:
        st.subheader("Team Tasks")
        
        if team_id:
            team_tasks = db_ops.get_team_tasks(team_id)
            
            if team_tasks:
                # Group by status
                statuses = ['todo', 'in_progress', 'completed']
                
                for status in statuses:
                    status_tasks = [t for t in team_tasks if t['status'] == status]
                    
                    if status_tasks:
                        st.subheader(f"{status.replace('_', ' ').title()} ({len(status_tasks)})")
                        
                        for task in status_tasks:
                            # Only show assigned name for team members
                            assignee = task.get('assigned_name', 'Unassigned')
                            
                            card_class = "task-card"
                            if task['priority'] == 'urgent':
                                card_class += " urgent-task"
                            
                            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                            
                            cols = st.columns([3, 1, 1])
                            with cols[0]:
                                st.write(f"**{task['title']}**")
                                if task['description']:
                                    st.caption(task['description'][:100] + "..." if len(task['description']) > 100 else task['description'])
                            with cols[1]:
                                st.write(f"👤 {assignee}")
                            with cols[2]:
                                priority_color = {
                                    'urgent': '#FF6B6B',
                                    'high': '#FFA94D',
                                    'medium': '#FFD166',
                                    'low': '#06D6A0'
                                }.get(task['priority'], '#8D99AE')
                                st.markdown(f'<span style="color:{priority_color};">{task["priority"].title()}</span>', 
                                          unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No team tasks found.")
        else:
            st.warning("You are not part of a team.")
    
    with tab3:
        st.subheader("Create New Task")
        
        with st.form("create_task_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Task Title*", placeholder="Enter task title")
                description = st.text_area("Description", placeholder="Enter task description", height=100)
            
            with col2:
                priority = st.selectbox("Priority", ["low", "medium", "high", "urgent"])
                deadline = st.date_input("Deadline", min_value=datetime.now().date())
            
            # For now, only assign to self. In Phase 3, we'll add team assignment
            assigned_to = user_id
            
            submit_button = st.form_submit_button("Create Task", type="primary")
            
            if submit_button:
                if not title:
                    st.error("Task title is required!")
                else:
                    task_id = db_ops.create_task(
                        title=title,
                        description=description,
                        assigned_to=assigned_to,
                        priority=priority,
                        deadline=deadline
                    )
                    
                    st.success(f"Task '{title}' created successfully!")
                    st.balloons()

def show_team_info():
    """Team Information Page"""
    st.title("👥 Team Information")
    
    user_id = st.session_state.user['id']
    team_id = st.session_state.user['team_id']
    
    if not team_id:
        st.warning("You are not part of a team yet.")
        
        # Create team option
        with st.expander("Create a Team"):
            team_name = st.text_input("Team Name")
            if st.button("Create Team"):
                if team_name:
                    new_team_id = db.db.create_team(team_name, user_id)
                    st.session_state.user['team_id'] = new_team_id
                    st.success(f"Team '{team_name}' created! Refreshing...")
                    time.sleep(2)
                    st.rerun()
        
        return
    
    # Get team information
    team_members = db_ops.get_team_members(team_id)
    team_stats = db_ops.get_team_stats(team_id)
    
    # Team Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Members", team_stats['total_members'])
    
    with col2:
        st.metric("Active Members", team_stats['active_members'])
    
    with col3:
        st.metric("Avg Team Mood", f"{team_stats['avg_mood']:.1f}/10")
    
    with col4:
        st.metric("Task Completion", f"{team_stats['completion_rate']}%")
    
    st.markdown("---")
    
    # Team Members
    st.subheader("Team Members")
    
    if team_members:
        for member in team_members:
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            with col1:
                role_emoji = "👑" if member['role'] == 'admin' else "👤"
                st.write(f"{role_emoji} **{member['username']}**")
                st.caption(member['email'])
            
            with col2:
                join_date = member['created_at']
                if isinstance(join_date, str):
                    join_date = datetime.strptime(join_date, '%Y-%m-%d %H:%M:%S')
                st.caption(f"Joined: {join_date.strftime('%b %d, %Y')}")
            
            with col3:
                st.write(f"**{member['role'].title()}**")
            
            with col4:
                # Get member's today's mood
                today_mood = db_ops.get_today_mood_stats(member['id'])
                if today_mood['avg_mood']:
                    mood_score = today_mood['avg_mood']
                    color = viz._get_mood_color(mood_score)
                    st.markdown(f'<span style="color:{color}; font-weight:bold;">{mood_score:.1f}/10</span>', 
                              unsafe_allow_html=True)
                else:
                    st.caption("No entry")
        
        st.markdown("---")
        
        # Team Activity
        st.subheader("Recent Team Activity")
        
        # Get recent mood entries
        conn = db.get_connection()
        query = '''
        SELECT u.username, me.text_entry, me.combined_score, me.created_at
        FROM mood_entries me
        JOIN users u ON me.user_id = u.id
        WHERE u.team_id = ?
        ORDER BY me.created_at DESC
        LIMIT 10
        '''
        
        import pandas as pd
        recent_activity = pd.read_sql_query(query, conn, params=(team_id,))
        conn.close()
        
        if not recent_activity.empty:
            for _, row in recent_activity.iterrows():
                cols = st.columns([1, 3, 1])
                with cols[0]:
                    st.write(f"**{row['username']}**")
                with cols[1]:
                    if row['text_entry']:
                        st.write(row['text_entry'][:100] + "..." if len(row['text_entry']) > 100 else row['text_entry'])
                with cols[2]:
                    score = row['combined_score']
                    color = viz._get_mood_color(score)
                    st.markdown(f'<span style="color:{color};">{score:.1f}</span>', 
                              unsafe_allow_html=True)
        else:
            st.info("No recent team activity")
    
    else:
        st.info("No team members found.")
def show_team_management():
    """Team Management page"""
    st.switch_page("pages/6_Team_Management.py")
    
def show_analytics():
    """Analytics Page"""
    st.title("📈 Analytics")
    
    user_id = st.session_state.user['id']
    team_id = st.session_state.user['team_id']
    
    if not team_id:
        st.warning("Analytics are available only for team members.")
        return
    
    # Tabs for different analytics
    tab1, tab2, tab3 = st.tabs(["Mood Analytics", "Productivity", "Team Insights"])
    
    with tab1:
        st.subheader("Mood Analytics")
        
        # Get mood history
        mood_history = db_ops.get_user_mood_history(user_id, days=30)
        
        if not mood_history.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                avg_mood = mood_history['avg_mood'].mean()
                st.metric("30-Day Avg Mood", f"{avg_mood:.1f}/10")
            
            with col2:
                mood_std = mood_history['avg_mood'].std()
                stability = "High" if mood_std < 1.5 else "Medium" if mood_std < 2.5 else "Low"
                st.metric("Mood Stability", stability, 
                         f"Std: {mood_std:.2f}")
            
            # Mood trend chart using our viz module
            fig = viz.create_mood_trend_chart(mood_history)
            st.plotly_chart(fig, use_container_width=True)
            
            # Mood distribution using Plotly Graph Objects instead of Plotly Express
            st.subheader("Mood Distribution")
            
            # Create histogram with Plotly Graph Objects
            import plotly.graph_objects as go
            
            # Create bins
            bins = list(range(1, 12))  # 1 to 11 for 1-10 scale
            hist_data = []
            
            for i in range(len(bins)-1):
                count = ((mood_history['avg_mood'] >= bins[i]) & 
                        (mood_history['avg_mood'] < bins[i+1])).sum()
                hist_data.append(count)
            
            # Create x labels (ranges)
            x_labels = [f"{bins[i]}-{bins[i+1]}" for i in range(len(bins)-1)]
            
            fig = go.Figure(data=[go.Bar(
                x=x_labels,
                y=hist_data,
                marker_color='#1E88E5',
                text=hist_data,
                textposition='auto',
            )])
            
            fig.update_layout(
                title="Frequency of Mood Scores",
                xaxis_title="Mood Score Range",
                yaxis_title="Frequency",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No mood data available for analytics")
    
    with tab2:
        st.subheader("Productivity Analytics")
        
        # Task statistics
        task_stats = db_ops.get_task_stats(user_id)
        
        if task_stats['total'] > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                completion_rate = task_stats['completion_rate']
                st.metric("Completion Rate", f"{completion_rate}%")
            
            with col2:
                # Calculate average days to complete (placeholder)
                avg_days = 2.5
                st.metric("Avg Time to Complete", f"{avg_days} days")
            
            with col3:
                # Calculate on-time completion
                total_completed = task_stats['completed']
                on_time_rate = 85  # Placeholder
                st.metric("On-Time Rate", f"{on_time_rate}%")
            
            # Task completion chart
            fig = viz.create_task_completion_chart(task_stats)
            st.plotly_chart(fig, use_container_width=True)
            
            # Productivity insights
            st.subheader("Productivity Insights")
            
            if completion_rate > 80:
                st.success("✅ **Excellent Productivity**: You're completing most of your tasks!")
                st.write("**Recommendations:**")
                st.write("1. Keep up the great work!")
                st.write("2. Consider mentoring team members")
                st.write("3. Share your productivity tips")
            elif completion_rate > 60:
                st.info("📊 **Good Productivity**: You're making steady progress.")
                st.write("**Recommendations:**")
                st.write("1. Focus on high-priority tasks")
                st.write("2. Break large tasks into smaller steps")
                st.write("3. Set daily goals")
            else:
                st.warning("⚠️ **Productivity Improvement Needed**")
                st.write("**Recommendations:**")
                st.write("1. Review task priorities")
                st.write("2. Eliminate distractions")
                st.write("3. Use time blocking technique")
            
        else:
            st.info("No task data available for productivity analytics")
    
    with tab3:
        st.subheader("Team Insights")
        
        team_stats = db_ops.get_team_stats(team_id)
        team_mood_summary = db_ops.get_team_mood_summary(team_id)
        
        if team_mood_summary:
            # Team overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Team Mood", f"{team_stats['avg_mood']:.1f}/10")
            
            with col2:
                st.metric("Team Stress", f"{team_stats['avg_stress']:.1f}/10")
            
            with col3:
                st.metric("Active Members", team_stats['active_members'])
            
            with col4:
                st.metric("Task Completion", f"{team_stats['completion_rate']}%")
            
            # Team member mood table
            st.subheader("Team Member Mood Summary")
            
            # Create a simple table
            table_data = []
            for member in team_mood_summary:
                table_data.append({
                    "Member": member['username'],
                    "Avg Mood": f"{member['avg_mood']:.1f}",
                    "Avg Stress": f"{member['avg_stress']:.1f}",
                    "Entries": member['total_entries']
                })
            
            # Display as dataframe
            import pandas as pd
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Team recommendations
            st.subheader("AI Team Recommendations")
            
            avg_team_mood = team_stats['avg_mood']
            avg_team_stress = team_stats['avg_stress']
            
            if avg_team_mood < 5:
                st.warning("⚠️ **Team Mood Alert**: Average team mood is low.")
                st.write("**Recommendations:**")
                st.write("1. Schedule a team check-in meeting")
                st.write("2. Consider workload redistribution")
                st.write("3. Organize a team-building activity")
            
            if avg_team_stress > 7:
                st.error("🚨 **High Stress Alert**: Team stress levels are elevated.")
                st.write("**Recommendations:**")
                st.write("1. Review deadlines and priorities")
                st.write("2. Encourage breaks and work-life balance")
                st.write("3. Consider implementing 'no-meeting' days")
            
            if avg_team_mood >= 7 and avg_team_stress <= 5:
                st.success("✅ **Team Status**: Optimal performance zone!")
                st.write("**Maintain this by:**")
                st.write("1. Continue regular check-ins")
                st.write("2. Recognize and celebrate achievements")
                st.write("3. Keep workloads balanced")
            
            if avg_team_mood >= 5 and avg_team_mood < 7 and avg_team_stress <= 6:
                st.info("📊 **Team Status**: Good performance, room for improvement.")
                st.write("**Suggestions:**")
                st.write("1. Regular mood check-ins")
                st.write("2. Clear communication channels")
                st.write("3. Regular feedback sessions")
        
        else:
            st.info("Not enough team data for insights. Encourage team members to track their mood!")

def show_settings():
    """Settings Page"""
    st.title("⚙️ Settings")
    
    user_id = st.session_state.user['id']
    user = db.get_user_by_id(user_id)
    
    if not user:
        st.error("User not found!")
        return
    
    # Tabs for different settings
    tab1, tab2, tab3, tab4 = st.tabs(["Profile", "Privacy", "Notifications", "Account"])    
    with tab1:
        st.subheader("Profile Settings")
        
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username", value=user['username'])
                email = st.text_input("Email", value=user['email'])
            
            with col2:
                current_role = user.get('role', 'member')
                st.write(f"**Current Role:** {current_role.title()}")
                
                # Role change (admin only feature - placeholder)
                if current_role == 'admin':
                    new_role = st.selectbox("Change Role", ["member", "admin"], index=0 if current_role == 'member' else 1)
                else:
                    st.info("Contact admin to change role")
            
            if st.form_submit_button("Update Profile"):
                # Update logic here
                st.success("Profile updated successfully!")
    
    with tab2:
        st.subheader("Privacy Settings")
        
        # Mood tracking privacy
        st.write("**Mood Tracking Privacy**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            allow_visual = st.checkbox(
                "Enable visual mood tracking", 
                value=st.session_state.get('allow_visual_tracking', True),
                help="Allow camera access for facial expression analysis"
            )
            
            share_with_team = st.selectbox(
                "Share mood data with team",
                ["Anonymous statistics only", "Managers only", "Full team", "Nobody"],
                index=0,
                help="Control who can see your mood data"
            )
        
        with col2:
            store_images = st.checkbox(
                "Store analyzed images",
                value=False,
                help="Images are deleted after analysis unless enabled"
            )
            
            auto_delete = st.number_input(
                "Auto-delete data after (days)",
                min_value=7,
                max_value=365,
                value=30,
                help="Personal data will be automatically deleted after this period"
            )
        
        # Data collection preferences
        st.write("**Data Collection Preferences**")
        
        data_cols = st.columns(3)
        with data_cols[0]:
            collect_text = st.checkbox("Collect text analysis", value=True)
        with data_cols[1]:
            collect_visual = st.checkbox("Collect visual analysis", value=allow_visual)
        with data_cols[2]:
            collect_behavioral = st.checkbox("Collect behavioral patterns", value=True)
        
        if st.button("Save Privacy Settings", type="primary"):
            # Update session state
            st.session_state.allow_visual_tracking = allow_visual
            
            # Update database
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET allow_visual_tracking = ? WHERE id = ?
            ''', (1 if allow_visual else 0, user_id))
            conn.commit()
            conn.close()
            
            st.success("Privacy settings saved!")
    
    with tab3:
        st.subheader("Account Settings")
        
        st.write("**Change Password**")
        
        with st.form("password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Change Password"):
                if new_password != confirm_password:
                    st.error("New passwords don't match!")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    # Verify current password
                    conn = db.db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
                    current_hash = cursor.fetchone()[0]
                    conn.close()
                    
                    if db.db.verify_password(current_password, current_hash):
                        # Update password
                        new_hash = db.db.hash_password(new_password)
                        conn = db.db.get_connection()
                        cursor = conn.cursor()
                        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_hash, user_id))
                        conn.commit()
                        conn.close()
                        
                        st.success("Password changed successfully!")
                    else:
                        st.error("Current password is incorrect")
        
        st.markdown("---")
        
        st.write("**Data Management**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export My Data"):
                st.info("Data export feature coming soon!")
        
        with col2:
            if st.button("Delete My Account", type="secondary"):
                st.warning("⚠️ This action cannot be undone!")
                confirm = st.checkbox("I understand this will delete all my data")
                
                if confirm and st.button("Confirm Deletion", type="primary"):
                    st.error("Account deletion feature will be implemented in Phase 3")

if __name__ == "__main__":
    main()