# 🚀 Getting Started with Universal AI Workspace

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** (Backend)
- **Node.js 18+** (Frontend)
- **PostgreSQL** (Database)
- **Docker & Docker Compose** (Recommended for easy setup)
- **Git**

## API Keys Required

You'll need the following API keys:

- **OpenAI API Key** - For LLM and embeddings ([Get it here](https://platform.openai.com/api-keys))
- **Anthropic API Key** (Optional) - For Claude models
- **Pinecone API Key** (Optional) - Alternative to ChromaDB

---

## Quick Start with Docker (Recommended)

The easiest way to get started is using Docker Compose, which sets up everything automatically.

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd universal-ai-workspace
```

### Step 2: Set Up Environment Variables

**Backend (.env file):**

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` and add your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here_change_in_production
```

**Frontend (.env.local file):**

```bash
cd ../frontend
cp .env.example .env.local
```

The default values should work for local development.

### Step 3: Start All Services

From the root directory:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- ChromaDB (port 8000)
- Backend API (port 8001)
- Frontend (port 3000)

### Step 4: Access the Application

Open your browser and go to:
```
http://localhost:3000
```

Create an account and start using your AI workspace!

---

## Manual Setup (Without Docker)

If you prefer not to use Docker, follow these steps:

### Backend Setup

1. **Install PostgreSQL and Redis**

For Windows:
- Download PostgreSQL from https://www.postgresql.org/download/
- Download Redis from https://github.com/microsoftarchive/redis/releases

2. **Create Database**

```bash
# Open PostgreSQL command line
psql -U postgres

# Create database
CREATE DATABASE universal_ai;
CREATE USER aiuser WITH PASSWORD 'aipassword';
GRANT ALL PRIVILEGES ON DATABASE universal_ai TO aiuser;
\q
```

3. **Set Up Python Environment**

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

4. **Configure Environment**

```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
DATABASE_URL=postgresql://aiuser:aipassword@localhost:5432/universal_ai
OPENAI_API_KEY=your_key_here
SECRET_KEY=your_secret_key_here
```

5. **Start ChromaDB (Vector Database)**

In a new terminal:
```bash
pip install chromadb
chroma run --path ./chromadb_data
```

6. **Run Backend**

```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8001
```

Backend will be available at: `http://localhost:8001`

API docs: `http://localhost:8001/docs`

### Frontend Setup

1. **Install Dependencies**

```bash
cd frontend
npm install
```

2. **Configure Environment**

```bash
cp .env.example .env.local
```

3. **Run Frontend**

```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

---

## 🎯 First Steps After Installation

### 1. Create an Account

- Go to `http://localhost:3000`
- Click "Get Started"
- Fill in your details
- You'll be automatically logged in

### 2. Upload Your First Document

- Go to "Documents" tab
- Click "Upload"
- Select a PDF, Word doc, or text file
- The system will automatically process and index it

### 3. Start a Conversation

- Go to "Chat" tab
- Ask a question about your document
- The Document Agent will retrieve relevant information

### 4. Try Different Agents

**For Code Analysis:**
```
Explain the authentication flow in this codebase
```

**For Documents:**
```
Summarize the key points from my uploaded document
```

**For Tasks:**
```
Help me break down my project into actionable tasks
```

**For Research:**
```
Explain quantum computing in simple terms
```

---

## 📱 Usage Examples

### Example 1: Code Analysis

1. Upload your code repository or individual files
2. Ask questions like:
   - "Find all functions that use authentication"
   - "Explain how the user registration works"
   - "Are there any security vulnerabilities?"

### Example 2: Document Q&A

1. Upload PDFs, Word docs, research papers
2. Ask questions like:
   - "What are the main conclusions in this paper?"
   - "Extract all action items from this meeting notes"
   - "Compare the findings across these three documents"

### Example 3: Task Management

Ask the AI:
- "Help me plan a website redesign project"
- "Break down learning Python into weekly goals"
- "Create a study schedule for my exams"

The Task Agent will create structured tasks with priorities and deadlines.

---

## 🔧 Configuration Options

### Backend Configuration

Edit `backend/.env`:

```env
# LLM Model
DEFAULT_LLM_MODEL=gpt-4-turbo-preview  # or gpt-3.5-turbo for faster/cheaper
DEFAULT_TEMPERATURE=0.7

# Embedding Model
EMBEDDING_MODEL=text-embedding-3-small  # or text-embedding-3-large

# File Upload
MAX_UPLOAD_SIZE=50000000  # 50MB

# Enable/Disable Agents
ENABLE_CODE_AGENT=True
ENABLE_DOCUMENT_AGENT=True
ENABLE_TASK_AGENT=True
ENABLE_RESEARCH_AGENT=True
```

### Vector Database Options

**Option 1: ChromaDB (Default - Local)**
```env
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

**Option 2: Pinecone (Cloud)**
```env
PINECONE_API_KEY=your_key
PINECONE_ENVIRONMENT=your_environment
```

---

## 🐛 Troubleshooting

### Backend won't start

1. **Database connection error**
   - Make sure PostgreSQL is running
   - Check DATABASE_URL in .env
   - Verify database exists

2. **Module not found error**
   - Activate virtual environment
   - Run: `pip install -r requirements.txt`

3. **OpenAI API error**
   - Verify your API key in .env
   - Check you have credits in your OpenAI account

### Frontend won't start

1. **Port already in use**
   ```bash
   # Change port
   npm run dev -- -p 3001
   ```

2. **API connection error**
   - Make sure backend is running on port 8001
   - Check NEXT_PUBLIC_API_URL in .env.local

### Document upload fails

1. Check file size (max 50MB by default)
2. Verify ChromaDB is running
3. Check backend logs for errors

### Chat not responding

1. Verify OpenAI API key is valid
2. Check backend logs for errors
3. Make sure all agents are enabled in .env

---

## 📊 System Requirements

### Minimum:
- RAM: 4GB
- Storage: 10GB
- CPU: 2 cores

### Recommended:
- RAM: 8GB+
- Storage: 50GB+ (for documents and vector DB)
- CPU: 4+ cores

---

## 🔐 Security Best Practices

1. **Change default credentials**
   - Update SECRET_KEY in backend/.env
   - Use strong database passwords

2. **API Keys**
   - Never commit .env files
   - Use environment-specific keys
   - Rotate keys regularly

3. **Production Deployment**
   - Enable HTTPS
   - Set DEBUG=False
   - Use production-grade databases
   - Set up proper authentication

---

## 📚 Next Steps

- [API Documentation](./API.md)
- [Architecture Guide](./ARCHITECTURE.md)
- [Contributing Guidelines](./CONTRIBUTING.md)
- [Deployment Guide](./DEPLOYMENT.md)

---

## 💬 Need Help?

- **Documentation**: Check the `/docs` folder
- **Issues**: [GitHub Issues](https://github.com/yourusername/universal-ai-workspace/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/universal-ai-workspace/discussions)

---

**Happy building with your Universal AI Workspace! 🚀**
