# 🧠 Team Optimizer AI

An intelligent **Streamlit-based web application** that helps teams optimize productivity, track mood, manage tasks, and analyze team dynamics using **AI-powered sentiment analysis** and visual analytics.

---

## 📋 Overview

Team Optimizer AI is a comprehensive team management platform that combines:
- **Mood Tracking** with text and visual sentiment analysis
- **Task Management** with priority levels and deadlines
- **Team Analytics** with interactive visualizations
- **User Authentication** with secure credential management
- **Team Management** for creating and organizing teams

---

## ✨ Key Features

### 🎭 Mood Tracker
- Submit daily mood updates with text entries
- **Dual Sentiment Analysis:**
  - Text-based sentiment using VADER and TextBlob
  - Visual sentiment analysis using DeepFace (facial emotion detection)
- Fusion engine that combines both analyses
- Historical mood tracking and trends

### 📋 Task Manager
- Create and manage tasks with priorities
- Set deadlines and track completion
- Filter tasks by status
- Task assignments to team members

### 👥 Team Management
- Create and manage teams
- Add/remove team members
- Role-based access control
- Team performance analytics

### 📊 Analytics Dashboard
- Interactive charts using Plotly
- Mood trend analysis over time
- Team productivity metrics
- Sentiment distribution visualizations
- Task completion analytics

### 🔐 Authentication
- Secure user registration and login
- Password hashing with bcrypt
- Session management
- User profile management

---

## 🛠️ Technology Stack

- **Frontend:** Streamlit
- **Backend:** Python, SQLite
- **ML/AI:**
  - DeepFace (facial emotion recognition)
  - VADER Sentiment Analysis
  - TextBlob NLP
  - TensorFlow/Keras
- **Visualization:** Plotly, Plotly Express
- **Security:** bcrypt password hashing
- **Computer Vision:** OpenCV

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+
- 8GB+ RAM (for TensorFlow models)
- Webcam (optional, for visual sentiment analysis)

### Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/Ankitbhaumik916/Task_optimizer_new.git
cd Task_optimizer_new
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Download NLTK data:**
```bash
python -m nltk.downloader vader_lexicon punkt
```

4. **Run the application:**
```bash
streamlit run app.py
```

5. **Access the app:**
   - Local: http://localhost:8501
   - Network: http://[your-ip]:8501

---

## 📦 Dependencies

```
streamlit==1.31.0
pandas==2.2.0
plotly==5.18.0
nltk==3.8.1
textblob==0.17.1
vaderSentiment==3.3.2
bcrypt==4.1.2
deepface
opencv-python==4.9.0.80
Pillow==10.2.0
numpy==1.26.3
tensorflow
tf-keras
```

---

## 🚀 Usage

### First Time Setup
1. Launch the application
2. **Register** a new account on the login page
3. Log in with your credentials

### Dashboard Features
- View overall team metrics
- Check recent mood entries
- Monitor task progress
- Access quick analytics

### Mood Tracking
1. Navigate to **Mood Tracker**
2. Enter text about your current mood
3. (Optional) Upload a photo for visual sentiment analysis
4. Submit to get AI-powered sentiment analysis

### Task Management
1. Go to **Task Manager**
2. Create new tasks with:
   - Task name
   - Description
   - Priority level
   - Deadline
3. Assign to team members
4. Track completion status

### Analytics
- Access **Analytics** page for:
  - Mood trends over time
  - Sentiment distribution
  - Task completion rates
  - Team performance metrics

---

## 📂 Project Structure

```
Task_optimizer_new/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── auth/
│   └── authentication.py       # User authentication logic
├── database/
│   ├── models.py              # Database models and schema
│   └── operations.py          # Database operations
├── pages/
│   ├── 1_Dashboard.py         # Dashboard page
│   ├── 2_Mood_Tracker.py      # Mood tracking interface
│   ├── 3_Task_Manager.py      # Task management
│   ├── 4_Team_Info.py         # Team information
│   ├── 5_Analytics.py         # Analytics visualizations
│   └── 6_Team_Management.py   # Team admin panel
└── utils/
    ├── sentiment_analyzer.py   # Text sentiment analysis
    ├── visual_sentiment.py     # Visual emotion detection
    ├── fusion_engine.py        # Multi-modal sentiment fusion
    └── visualizations.py       # Chart and graph utilities
```

---

## 🧪 AI/ML Components

### Text Sentiment Analysis
- **VADER:** Optimized for social media and short texts
- **TextBlob:** General-purpose sentiment polarity
- Combines both for robust text sentiment

### Visual Sentiment Analysis
- **DeepFace:** Pre-trained deep learning model
- Detects 7 emotions: Happy, Sad, Angry, Surprise, Fear, Disgust, Neutral
- Facial recognition and emotion classification

### Fusion Engine
- Intelligently combines text and visual sentiment
- Weighted average based on confidence scores
- Adaptive learning from user feedback

---

## 🔒 Security Features

- Password hashing using bcrypt
- Session-based authentication
- SQL injection prevention
- Secure credential storage
- User data isolation

---

## 📊 Database Schema

- **Users:** Authentication and profile data
- **Moods:** Mood entries with sentiment scores
- **Tasks:** Task details, assignments, status
- **Teams:** Team structure and membership
- **Analytics:** Aggregated metrics and trends

---

## 🎯 Future Enhancements

- [ ] Real-time team collaboration features
- [ ] Advanced analytics with predictive modeling
- [ ] Export reports to PDF/Excel
- [ ] Slack/Teams integration
- [ ] Mobile app version
- [ ] Multi-language support
- [ ] Custom sentiment models

---

## 📄 License

MIT License - Feel free to use and modify for your needs.

---

## 👨‍💻 Author

**Ankit Bhaumik**
- GitHub: [@Ankitbhaumik916](https://github.com/Ankitbhaumik916)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## ⚠️ Notes

- TensorFlow models will download on first run (~500MB)
- Webcam access required for visual sentiment analysis
- SQLite database created automatically on first run
- Compatible with Windows, macOS, and Linux

---

**Built with ❤️ using Streamlit and AI**
