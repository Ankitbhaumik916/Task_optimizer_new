# 🚀 Quick Start Guide - Team Optimizer Pro Rebuild

## Step-by-Step Setup Instructions

---

## Option 1: Complete New Project (Recommended)

### 1. Create New Project Structure

```bash
# Navigate to parent directory
cd D:\TOP

# Create new project
mkdir TeamOptimizer-Pro
cd TeamOptimizer-Pro

# Initialize Git
git init
echo "node_modules/" > .gitignore
echo ".env" >> .gitignore
echo "*.db" >> .gitignore
echo "__pycache__/" >> .gitignore
```

### 2. Setup Backend (Node.js + Express + TypeScript)

```bash
# Create backend directory
mkdir backend
cd backend

# Initialize Node.js project
npm init -y

# Install dependencies
npm install express cors dotenv bcryptjs jsonwebtoken
npm install @prisma/client express-validator socket.io

# Install dev dependencies
npm install -D typescript @types/express @types/node @types/bcryptjs
npm install -D @types/jsonwebtoken ts-node-dev nodemon prisma

# Initialize TypeScript
npx tsc --init

# Initialize Prisma
npx prisma init
```

#### TypeScript Configuration (`tsconfig.json`)
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

#### Package.json Scripts
```json
{
  "scripts": {
    "dev": "ts-node-dev --respawn --transpile-only src/server.ts",
    "build": "tsc",
    "start": "node dist/server.js",
    "prisma:generate": "prisma generate",
    "prisma:migrate": "prisma migrate dev",
    "prisma:studio": "prisma studio"
  }
}
```

### 3. Setup Frontend (Next.js + TypeScript + Tailwind)

```bash
# Navigate back to project root
cd ..

# Create Next.js app with TypeScript
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir

cd frontend

# Install additional dependencies
npm install axios zustand @tanstack/react-query
npm install recharts date-fns
npm install lucide-react class-variance-authority clsx tailwind-merge

# Install shadcn/ui
npx shadcn-ui@latest init

# Add shadcn components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add form
npx shadcn-ui@latest add input
npx shadcn-ui@latest add label
npx shadcn-ui@latest add select
npx shadcn-ui@latest add table
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add toast
```

### 4. Setup ML Service (Python FastAPI)

```bash
# Navigate back to project root
cd ..

# Create ML service directory
mkdir ml-service
cd ml-service

# Create virtual environment
python -m venv venv

# Activate venv (Windows)
venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn python-multipart
pip install deepface opencv-python pillow numpy
pip install textblob vaderSentiment nltk
pip install python-dotenv pydantic

# Create requirements.txt
pip freeze > requirements.txt
```

### 5. Setup Database (PostgreSQL)

```bash
# Install PostgreSQL (if not installed)
# Download from: https://www.postgresql.org/download/

# Or use Docker
docker run --name team-optimizer-db -e POSTGRES_PASSWORD=yourpassword -e POSTGRES_DB=teamoptimizer -p 5432:5432 -d postgres:15
```

### 6. Environment Variables

#### Backend `.env`
```env
NODE_ENV=development
PORT=5000

# Database
DATABASE_URL="postgresql://postgres:yourpassword@localhost:5432/teamoptimizer?schema=public"

# JWT Secrets
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_REFRESH_SECRET=your-refresh-secret-key
JWT_EXPIRE=15m
JWT_REFRESH_EXPIRE=7d

# ML Service
ML_SERVICE_URL=http://localhost:8000

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
```

#### Frontend `.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:5000/api
NEXT_PUBLIC_WS_URL=http://localhost:5000
```

#### ML Service `.env`
```env
API_PORT=8000
BACKEND_URL=http://localhost:5000
```

---

## Project Structure Creation

### Backend Structure

```bash
cd backend
mkdir -p src/{controllers,routes,middleware,services,utils,config,types}
mkdir -p prisma
```

Create these files:

#### `src/server.ts` (Entry point)
```typescript
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors({
  origin: process.env.FRONTEND_URL,
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Routes (to be added)
app.get('/api', (req, res) => {
  res.json({ message: 'Team Optimizer API' });
});

// Error handling
app.use((err: any, req: any, res: any, next: any) => {
  console.error(err.stack);
  res.status(500).json({ 
    error: 'Something went wrong!', 
    message: err.message 
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});
```

#### `prisma/schema.prisma` (Copy from REBUILD_PLAN.md)
```prisma
// Copy the entire schema from REBUILD_PLAN.md
```

### Frontend Structure

```bash
cd ../frontend
mkdir -p app/{(auth)/{login,signup},(dashboard)/{dashboard,tasks,mood,team,analytics},api}
mkdir -p components/{ui,auth,dashboard,tasks,mood,team}
mkdir -p lib
mkdir -p hooks
mkdir -p store
mkdir -p types
```

#### `lib/api.ts` (API Client)
```typescript
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### ML Service Structure

```bash
cd ../ml-service
mkdir -p app/{routers,services,models}
```

#### `app/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Team Optimizer ML Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "ML Service Running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Docker Setup (Optional but Recommended)

### `docker-compose.yml` (Project Root)
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: yourpassword
      POSTGRES_DB: teamoptimizer
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://postgres:yourpassword@postgres:5432/teamoptimizer
      ML_SERVICE_URL: http://ml-service:8000
    depends_on:
      - postgres
    volumes:
      - ./backend:/app
      - /app/node_modules

  ml-service:
    build: ./ml-service
    ports:
      - "8000:8000"
    volumes:
      - ./ml-service:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:5000/api
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next

volumes:
  postgres_data:
```

---

## Running the Project

### Development Mode

```bash
# Terminal 1 - Backend
cd backend
npm run dev

# Terminal 2 - Frontend
cd frontend
npm run dev

# Terminal 3 - ML Service
cd ml-service
venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000

# Terminal 4 - Database (if using Docker)
docker-compose up postgres
```

### With Docker Compose

```bash
# From project root
docker-compose up --build
```

---

## Initial Database Setup

```bash
cd backend

# Generate Prisma Client
npx prisma generate

# Create migration
npx prisma migrate dev --name init

# Open Prisma Studio (optional)
npx prisma studio
```

---

## Verification Checklist

- [ ] Backend running on http://localhost:5000
- [ ] Frontend running on http://localhost:3000
- [ ] ML Service running on http://localhost:8000
- [ ] PostgreSQL running on localhost:5432
- [ ] All services can communicate
- [ ] Database schema created
- [ ] Environment variables configured

---

## Next Steps After Setup

1. **Implement Authentication**
   - JWT middleware
   - Login/Signup endpoints
   - Protected routes

2. **Implement RBAC**
   - Role middleware
   - Permission checking
   - Team role assignment

3. **Build Core Features**
   - Team management
   - Task management
   - Mood tracking

4. **Integrate ML Service**
   - Text sentiment endpoint
   - Visual sentiment endpoint
   - Fusion engine

5. **Polish UI**
   - Responsive design
   - Loading states
   - Error handling

---

## Helpful Commands Reference

```bash
# Backend
npm run dev              # Start dev server
npm run build            # Build for production
npx prisma migrate dev   # Create migration
npx prisma studio        # Open database GUI

# Frontend
npm run dev              # Start dev server
npm run build            # Build for production
npm run lint             # Run linter

# ML Service
python -m uvicorn app.main:app --reload  # Start dev server

# Docker
docker-compose up        # Start all services
docker-compose down      # Stop all services
docker-compose logs -f   # View logs
```

---

## Resources & Documentation

- **Next.js:** https://nextjs.org/docs
- **Prisma:** https://www.prisma.io/docs
- **FastAPI:** https://fastapi.tiangolo.com/
- **shadcn/ui:** https://ui.shadcn.com/
- **Tailwind CSS:** https://tailwindcss.com/docs

---

**Ready to build! Need help with any specific part?** 🚀
