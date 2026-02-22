# 🚀 Team Optimizer AI - Full Stack Rebuild Plan

## 📊 Current State Analysis

### ✅ What Currently Exists:
1. **Authentication** ✓
   - Basic login/signup with bcrypt
   - User sessions (Streamlit-based)
   - Email uniqueness validation

2. **Team Management** ✓ (Partial)
   - Team creation
   - Basic team joining
   - Team ID system
   - ❌ Missing: Proper roles, permissions, team codes

3. **Mood Tracking** ✓
   - Text sentiment (VADER + TextBlob)
   - Visual sentiment (DeepFace)
   - Fusion engine
   - Mood history

4. **Database** ✓
   - SQLite with basic schema
   - Users, Teams, Mood Entries, Tasks tables

5. **Task Management** ✓ (Basic)
   - Task creation
   - Status tracking
   - ❌ Missing: Assignment system, leader control

### ❌ What's Missing or Needs Improvement:

1. **Proper Full-Stack Architecture**
   - No REST API backend
   - Streamlit is not scalable for production
   - No frontend framework (React/Vue/Next.js)

2. **Role-Based Access Control (RBAC)**
   - No leader/admin distinction
   - No permission system
   - No task creation restrictions

3. **Advanced Team Management**
   - No team invite system
   - No member designation/roles
   - No team analytics by role

4. **Task Assignment System**
   - Can't assign tasks to specific members
   - No leader-only task creation
   - No task delegation workflow

5. **Professional Features**
   - No real-time updates
   - No notifications
   - No API documentation
   - No proper error handling
   - No unit tests

---

## 🏗️ Proposed Architecture

### **Tech Stack**

#### **Frontend:**
```
- React.js + TypeScript
- Next.js 14 (App Router)
- Tailwind CSS + shadcn/ui
- Zustand for state management
- React Query for API calls
- Chart.js / Recharts for visualizations
- Socket.io-client for real-time updates
```

#### **Backend:**
```
- Node.js + Express.js + TypeScript
- PostgreSQL (instead of SQLite)
- Prisma ORM
- JWT + bcrypt for authentication
- Socket.io for WebSocket
- Express-validator for validation
- Swagger/OpenAPI for documentation
```

#### **ML Services:**
```
- Python FastAPI microservice
- DeepFace for visual sentiment
- TextBlob + VADER for text sentiment
- Separate service for AI processing
```

#### **DevOps:**
```
- Docker + Docker Compose
- GitHub Actions for CI/CD
- Environment configs
```

---

## 📁 New Project Structure

```
team-optimizer-pro/
│
├── frontend/                       # Next.js Frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   └── signup/
│   │   │   ├── (dashboard)/
│   │   │   │   ├── dashboard/
│   │   │   │   ├── mood-tracker/
│   │   │   │   ├── tasks/
│   │   │   │   ├── team/
│   │   │   │   └── analytics/
│   │   │   └── api/                # Next.js API routes (optional)
│   │   ├── components/
│   │   │   ├── ui/                 # shadcn components
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── mood/
│   │   │   ├── tasks/
│   │   │   └── team/
│   │   ├── lib/
│   │   │   ├── api.ts             # API client
│   │   │   ├── auth.ts            # Auth utilities
│   │   │   └── utils.ts
│   │   ├── hooks/
│   │   ├── store/                  # Zustand stores
│   │   └── types/                  # TypeScript types
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                        # Express.js Backend
│   ├── src/
│   │   ├── controllers/
│   │   │   ├── auth.controller.ts
│   │   │   ├── team.controller.ts
│   │   │   ├── task.controller.ts
│   │   │   ├── mood.controller.ts
│   │   │   └── user.controller.ts
│   │   ├── routes/
│   │   │   ├── auth.routes.ts
│   │   │   ├── team.routes.ts
│   │   │   ├── task.routes.ts
│   │   │   └── mood.routes.ts
│   │   ├── middleware/
│   │   │   ├── auth.middleware.ts
│   │   │   ├── rbac.middleware.ts
│   │   │   └── validation.middleware.ts
│   │   ├── models/                 # Prisma models
│   │   ├── services/
│   │   │   ├── auth.service.ts
│   │   │   ├── team.service.ts
│   │   │   ├── task.service.ts
│   │   │   └── mood.service.ts
│   │   ├── utils/
│   │   │   ├── jwt.ts
│   │   │   ├── bcrypt.ts
│   │   │   └── errors.ts
│   │   ├── config/
│   │   │   ├── database.ts
│   │   │   └── config.ts
│   │   └── server.ts
│   ├── prisma/
│   │   └── schema.prisma
│   ├── package.json
│   └── tsconfig.json
│
├── ml-service/                     # Python ML Microservice
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app
│   │   ├── routers/
│   │   │   ├── sentiment.py
│   │   │   └── visual.py
│   │   ├── services/
│   │   │   ├── text_analyzer.py
│   │   │   ├── visual_analyzer.py
│   │   │   └── fusion_engine.py
│   │   └── models/
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
├── README.md
└── DEPLOYMENT.md
```

---

## 🗄️ Enhanced Database Schema (Prisma)

```prisma
// schema.prisma

model User {
  id                    String      @id @default(uuid())
  email                 String      @unique
  username              String      @unique
  passwordHash          String
  fullName              String?
  avatar                String?
  designation           String?     // Job title/role
  department            String?
  
  // Team relationship
  teamId                String?
  team                  Team?       @relation(fields: [teamId], references: [id])
  teamRole              TeamRole    @default(MEMBER)
  
  // Privacy settings
  allowVisualTracking   Boolean     @default(true)
  profileVisibility     Visibility  @default(TEAM)
  
  // Timestamps
  createdAt             DateTime    @default(now())
  updatedAt             DateTime    @updatedAt
  lastLoginAt           DateTime?
  
  // Relations
  createdTeams          Team[]      @relation("TeamCreator")
  assignedTasks         Task[]      @relation("AssignedTo")
  createdTasks          Task[]      @relation("CreatedBy")
  moodEntries           MoodEntry[]
  notifications         Notification[]
  
  @@index([email])
  @@index([teamId])
}

model Team {
  id              String       @id @default(uuid())
  name            String
  description     String?
  teamCode        String       @unique  // 6-char invite code
  avatar          String?
  
  // Creator/Admin
  createdById     String
  createdBy       User         @relation("TeamCreator", fields: [createdById], references: [id])
  
  // Settings
  isActive        Boolean      @default(true)
  maxMembers      Int          @default(50)
  allowJoinByCode Boolean      @default(true)
  
  // Timestamps
  createdAt       DateTime     @default(now())
  updatedAt       DateTime     @updatedAt
  
  // Relations
  members         User[]
  tasks           Task[]
  moodAnalytics   TeamMoodAnalytics[]
  
  @@index([teamCode])
  @@index([createdById])
}

model Task {
  id              String       @id @default(uuid())
  title           String
  description     String?
  status          TaskStatus   @default(TODO)
  priority        Priority     @default(MEDIUM)
  
  // Assignment
  assignedToId    String?
  assignedTo      User?        @relation("AssignedTo", fields: [assignedToId], references: [id])
  
  createdById     String
  createdBy       User         @relation("CreatedBy", fields: [createdById], references: [id])
  
  teamId          String
  team            Team         @relation(fields: [teamId], references: [id])
  
  // Task details
  tags            String[]
  deadline        DateTime?
  estimatedHours  Float?
  actualHours     Float?
  
  // Timestamps
  createdAt       DateTime     @default(now())
  updatedAt       DateTime     @updatedAt
  completedAt     DateTime?
  startedAt       DateTime?
  
  @@index([assignedToId])
  @@index([teamId])
  @@index([status])
}

model MoodEntry {
  id                String       @id @default(uuid())
  userId            String
  user              User         @relation(fields: [userId], references: [id])
  
  // Text analysis
  textEntry         String?
  textSentiment     Float?       // -1 to 1
  textEmotions      Json?
  
  // Visual analysis
  hasImage          Boolean      @default(false)
  visualSentiment   Float?       // -1 to 1
  detectedEmotion   String?
  emotionScores     Json?
  
  // Combined analysis
  combinedScore     Float        // 0-10 scale
  stressLevel       Int          // 1-10 scale
  energyLevel       Int?         // 1-10 scale
  
  // Metadata
  workContext       String?      // What they were working on
  tags              String[]
  isPrivate         Boolean      @default(false)
  
  createdAt         DateTime     @default(now())
  
  @@index([userId])
  @@index([createdAt])
}

model TeamMoodAnalytics {
  id              String       @id @default(uuid())
  teamId          String
  team            Team         @relation(fields: [teamId], references: [id])
  
  date            DateTime
  averageMood     Float
  averageStress   Float
  totalEntries    Int
  
  // Breakdown by role
  moodByRole      Json
  
  createdAt       DateTime     @default(now())
  
  @@unique([teamId, date])
  @@index([teamId])
}

model Notification {
  id              String       @id @default(uuid())
  userId          String
  user            User         @relation(fields: [userId], references: [id])
  
  type            NotificationType
  title           String
  message         String
  link            String?
  
  isRead          Boolean      @default(false)
  
  createdAt       DateTime     @default(now())
  
  @@index([userId])
  @@index([isRead])
}

// Enums
enum TeamRole {
  ADMIN      // Team creator, full control
  LEADER     // Can create/assign tasks, view all analytics
  MEMBER     // Can complete tasks, submit mood
  VIEWER     // Read-only access
}

enum TaskStatus {
  TODO
  IN_PROGRESS
  IN_REVIEW
  COMPLETED
  CANCELLED
}

enum Priority {
  LOW
  MEDIUM
  HIGH
  URGENT
}

enum Visibility {
  PRIVATE
  TEAM
  PUBLIC
}

enum NotificationType {
  TASK_ASSIGNED
  TASK_COMPLETED
  TEAM_INVITE
  MOOD_ALERT
  SYSTEM
}
```

---

## 🔌 API Endpoints

### **Authentication**
```
POST   /api/auth/signup            - Register new user
POST   /api/auth/login             - Login user
POST   /api/auth/logout            - Logout user
POST   /api/auth/refresh           - Refresh JWT token
GET    /api/auth/me                - Get current user
PUT    /api/auth/profile           - Update profile
POST   /api/auth/change-password   - Change password
```

### **Teams**
```
POST   /api/teams                  - Create team (anyone)
GET    /api/teams/:id              - Get team details
PUT    /api/teams/:id              - Update team (admin only)
DELETE /api/teams/:id              - Delete team (admin only)
POST   /api/teams/join             - Join team by code
GET    /api/teams/:id/members      - Get team members
POST   /api/teams/:id/members      - Add member (admin/leader)
DELETE /api/teams/:id/members/:userId - Remove member
PUT    /api/teams/:id/members/:userId/role - Update member role
GET    /api/teams/:id/analytics    - Get team analytics
```

### **Tasks**
```
POST   /api/tasks                  - Create task (leader/admin)
GET    /api/tasks                  - Get tasks (filtered)
GET    /api/tasks/:id              - Get task details
PUT    /api/tasks/:id              - Update task
DELETE /api/tasks/:id              - Delete task (creator/admin)
POST   /api/tasks/:id/assign       - Assign task to member
PUT    /api/tasks/:id/status       - Update task status
GET    /api/tasks/my-tasks         - Get my assigned tasks
GET    /api/tasks/team/:teamId     - Get team tasks
```

### **Mood Tracking**
```
POST   /api/mood                   - Submit mood entry
GET    /api/mood/my-history        - Get my mood history
GET    /api/mood/team/:teamId      - Get team mood (leader/admin)
POST   /api/mood/analyze-text      - Analyze text sentiment
POST   /api/mood/analyze-image     - Analyze facial emotion
GET    /api/mood/insights          - Get personalized insights
```

### **Analytics**
```
GET    /api/analytics/team/:teamId/overview     - Team overview
GET    /api/analytics/team/:teamId/mood         - Mood trends
GET    /api/analytics/team/:teamId/productivity - Task analytics
GET    /api/analytics/member/:userId            - Member analytics
```

---

## 🎨 Frontend Features

### **Pages & Components**

#### 1. **Authentication**
- Modern login/signup forms
- Social auth (optional)
- Email verification
- Password reset flow

#### 2. **Onboarding**
- Profile setup
- Team creation/join wizard
- Role selection
- Tutorial walkthrough

#### 3. **Dashboard** (Role-based views)
- **Admin/Leader View:**
  - Team overview metrics
  - Member mood heatmap
  - Task distribution
  - Alert notifications
  
- **Member View:**
  - My tasks
  - My mood history
  - Team updates
  - Personal insights

#### 4. **Team Management**
- Member directory with avatars
- Role badges
- Invite system with QR code
- Member performance cards
- Export reports

#### 5. **Task Manager**
- Kanban board (drag & drop)
- Calendar view
- Task filters (status, priority, assignee)
- Task creation modal (leader only)
- Bulk assignment
- Task dependencies

#### 6. **Mood Tracker**
- Emoji-based quick entry
- Text input with real-time sentiment
- Camera capture for visual analysis
- Mood calendar view
- Trend charts
- Comparative analytics

#### 7. **Analytics Dashboard**
- Interactive charts (Chart.js/Recharts)
- Date range filters
- Export to PDF/Excel
- Real-time updates
- Drill-down capabilities

---

## 🔐 Security & RBAC Implementation

### **Permission Matrix**

| Feature | Viewer | Member | Leader | Admin |
|---------|--------|--------|--------|-------|
| View team | ✓ | ✓ | ✓ | ✓ |
| Submit mood | ✗ | ✓ | ✓ | ✓ |
| View own mood | ✗ | ✓ | ✓ | ✓ |
| View team mood | ✗ | ✗ | ✓ | ✓ |
| Create tasks | ✗ | ✗ | ✓ | ✓ |
| Assign tasks | ✗ | ✗ | ✓ | ✓ |
| Complete tasks | ✗ | ✓ | ✓ | ✓ |
| View analytics | ✗ | Own only | Team | Team |
| Invite members | ✗ | ✗ | ✓ | ✓ |
| Manage roles | ✗ | ✗ | ✗ | ✓ |
| Delete team | ✗ | ✗ | ✗ | ✓ |

### **Middleware Implementation**
```typescript
// auth.middleware.ts - JWT verification
// rbac.middleware.ts - Role checking
// validation.middleware.ts - Input validation
```

---

## 🚀 Implementation Roadmap

### **Phase 1: Backend Foundation** (Week 1)
- [ ] Setup Express + TypeScript project
- [ ] Configure PostgreSQL + Prisma
- [ ] Implement authentication (JWT + bcrypt)
- [ ] Create API routes structure
- [ ] Implement RBAC middleware
- [ ] Add input validation
- [ ] Setup error handling

### **Phase 2: Core Features** (Week 2)
- [ ] Team management APIs
- [ ] Task management APIs
- [ ] User management APIs
- [ ] Mood tracking APIs
- [ ] Integrate ML service
- [ ] Add WebSocket support

### **Phase 3: Frontend Development** (Week 3)
- [ ] Setup Next.js + TypeScript
- [ ] Implement auth flow
- [ ] Build dashboard layouts
- [ ] Create team pages
- [ ] Build task manager (Kanban)
- [ ] Implement mood tracker UI
- [ ] Add analytics pages

### **Phase 4: ML Integration** (Week 4)
- [ ] Port Python ML code to FastAPI
- [ ] Text sentiment endpoint
- [ ] Visual sentiment endpoint
- [ ] Fusion engine
- [ ] Real-time processing

### **Phase 5: Polish & Professional Features** (Week 5)
- [ ] Real-time notifications
- [ ] Export functionality
- [ ] Dark mode
- [ ] Responsive design
- [ ] API documentation (Swagger)
- [ ] Unit tests
- [ ] Error boundaries

### **Phase 6: Deployment** (Week 6)
- [ ] Docker containerization
- [ ] Environment configs
- [ ] CI/CD pipeline
- [ ] Production database
- [ ] Monitoring & logging
- [ ] Demo data seeding

---

## 📱 Professional UI/UX Improvements

### **Design Principles:**
1. **Modern & Clean:** Use Tailwind + shadcn/ui
2. **Responsive:** Mobile-first approach
3. **Accessible:** WCAG 2.1 AA compliance
4. **Performant:** Lazy loading, code splitting
5. **Intuitive:** Clear navigation, tooltips

### **Key UI Components:**
- Professional color scheme (dark mode support)
- Loading skeletons
- Toast notifications
- Modal dialogs
- Dropdown menus
- Data tables with sorting/filtering
- Interactive charts
- Progress indicators
- Avatar with badges
- Status indicators

---

## 🧪 Testing Strategy

```
- Jest for unit tests
- React Testing Library for component tests
- Supertest for API tests
- Playwright for E2E tests
- Test coverage > 80%
```

---

## 📊 Hackathon Presentation Highlights

### **Technical Highlights:**
✓ Full-stack TypeScript architecture
✓ Microservices with Python ML service
✓ Real-time updates with WebSockets
✓ Role-based access control
✓ Dual sentiment analysis (text + visual)
✓ Professional UI with modern frameworks
✓ Docker containerization
✓ API documentation

### **Business Value:**
✓ Team wellness monitoring
✓ Productivity optimization
✓ Early burnout detection
✓ Data-driven insights
✓ Scalable architecture
✓ Privacy-focused

### **Innovation:**
✓ Fusion engine (text + visual sentiment)
✓ Real-time mood heatmaps
✓ Predictive analytics
✓ Automated task assignment suggestions
✓ Mood-based workload balancing

---

## 💡 Additional Feature Ideas

1. **AI Assistant:** Chat-based task assignment
2. **Mood-based Recommendations:** Break suggestions when stressed
3. **Gamification:** Points, badges, leaderboards
4. **Integrations:** Slack, Microsoft Teams, Google Calendar
5. **Mobile App:** React Native version
6. **Advanced Analytics:** ML predictions, trend forecasting
7. **Wellness Tips:** Based on mood patterns
8. **Team Building:** Suggestion engine for team activities

---

## 📝 Next Steps

1. **Review this plan** and identify priorities
2. **Choose tech stack** (confirm Node.js + React)
3. **Setup repositories** (monorepo or separate)
4. **Create project structure**
5. **Start with backend authentication**
6. **Build incrementally**

---

**Ready to build a hackathon-winning project! 🏆**
