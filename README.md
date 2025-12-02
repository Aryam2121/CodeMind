# CodeMind

> **Production-Ready RAG + LangChain + MCP Platform for Developers**

CodeMind is a powerful AI-powered knowledge assistant that uses Retrieval-Augmented Generation (RAG), LangChain, and Model Context Protocol (MCP) to help developers search, analyze, and understand codebases, documentation, and technical content.

![CodeMind Banner](https://img.shields.io/badge/AI-Powered-blue) ![Python](https://img.shields.io/badge/Python-3.10+-green) ![Next.js](https://img.shields.io/badge/Next.js-14-black) ![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal)

## 🚀 What's New in CodeMind

### ✨ **8 Major Features Added**

1. **🔗 GitHub Repository Analysis** - Index entire repos with one URL
2. **📁 Multi-File Batch Processing** - Upload multiple files simultaneously  
3. **💾 Conversation History** - SQLite-powered persistent memory
4. **🎨 Syntax Highlighting** - Auto-detects 20+ programming languages
5. **🔍 Advanced Search Filters** - Semantic, keyword, and hybrid modes
6. **⚙️ Real OpenAI Integration** - Multiple models with cost tracking
7. **📊 Settings Dashboard** - Configure LLM parameters dynamically
8. **📤 Export Functionality** - JSON, Markdown, TXT exports

## 📚 Key Features

### **Multi-Source Knowledge Ingestion**
- ✅ GitHub Repository Import (analyze entire repos)
- ✅ Local Directory Scanning (index your codebase)
- ✅ Document Upload (PDF, DOCX, TXT)
- ✅ Batch Processing (multiple files at once)
- ✅ Smart Filtering (ignores node_modules, .git, etc.)

### **Intelligent Q&A**
- ✅ Multi-Agent RAG (specialized agents)
- ✅ Source Citations (every answer referenced)
- ✅ Code Detection (auto-formats code blocks)
- ✅ Syntax Highlighting (20+ languages)
- ✅ Conversation Memory (context-aware)

### **Advanced Search**
- ✅ Semantic Search (understands meaning)
- ✅ Keyword Search (exact matching)
- ✅ Hybrid Mode (best of both)
- ✅ Metadata Filters (file type, repo, tags)
- ✅ Top-K Control (1-10 results)

### **Conversation Management**
- ✅ SQLite Database (persistent storage)
- ✅ Session Tracking (organized chats)
- ✅ Search History (find past conversations)
- ✅ Auto-Titling (smart naming)
- ✅ Usage Stats (analytics)

### **Export Capabilities**
- ✅ JSON Export (machine-readable)
- ✅ Markdown Export (formatted docs)
- ✅ Plain Text Export (simple files)
- ✅ CSV Reports (conversation lists)
- ✅ Summary Statistics (per conversation)

### **Configurable LLM**
- ✅ Multiple Models (GPT-4, GPT-3.5-turbo)
- ✅ Temperature Control (0.0-2.0)
- ✅ Max Tokens (response length)
- ✅ Streaming Support (real-time)
- ✅ Cost Estimation (API tracking)
- ✅ Mock Mode (free development)

## 🏗️ Architecture

```
CodeMind/
├── python-agent/              # Backend (FastAPI + LangChain)
│   ├── app.py                # Main API (460 lines, 20+ endpoints)
│   ├── rag.py                # RAG pipeline
│   ├── agents.py             # Multi-agent orchestrator
│   ├── vector_store.py       # Chroma DB wrapper
│   ├── github_loader.py      # NEW: GitHub repo loader
│   ├── conversation_manager.py  # NEW: SQLite conversations
│   ├── code_formatter.py     # NEW: Syntax highlighting
│   ├── export_manager.py     # NEW: Export functionality
│   ├── llm_config.py         # NEW: LLM configuration
│   └── models.py             # Pydantic models
│
├── frontend/                 # Next.js UI (fully redesigned)
│   ├── app/
│   │   ├── chat/            # AI chat with code highlighting
│   │   ├── map/             # Complaint visualization
│   │   ├── documents/       # Upload management
│   │   └── dashboard/       # Admin panel with stats
│   └── public/
│
├── test-data/               # Sample data
│   ├── documents/           # Policy docs
│   └── complaints.csv       # Geo data
│
└── conversations.db         # NEW: SQLite conversation history
```

## 📦 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git
- OpenAI API key (optional - has mock mode)

### 1. Clone & Install

```bash
git clone https://github.com/Aryam2121/CodeMind.git
cd CodeMind

# Backend
cd python-agent
pip install -r requirements.txt

# Frontend  
cd ../frontend
npm install
```

### 2. Configure

```bash
# Create .env in python-agent/
cat > python-agent/.env << EOF
OPENAI_API_KEY=your_key_here
USE_MOCK_LLM=false
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.7
PYTHON_AGENT_PORT=8000
EOF
```

### 3. Run

```bash
# Terminal 1: Backend
cd python-agent
python app.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 4. Access

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

## 🔧 API Endpoints

### 📥 **Ingestion**

#### Upload File
```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@document.pdf" \
  -F 'metadata={"tags": ["api", "docs"]}'
```

#### Import GitHub Repo
```bash
curl -X POST http://localhost:8000/ingest/github \
  -d "repo_url=https://github.com/user/repo" \
  -d "branch=main"
```

#### Index Local Directory
```bash
curl -X POST http://localhost:8000/ingest/local \
  -d "directory_path=/path/to/code"
```

### 💬 **Query**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does authentication work?",
    "top_k": 4,
    "filters": {"file_type": ".py"},
    "search_mode": "hybrid",
    "session_id": "my-session-123"
  }'
```

Response:
```json
{
  "answer": "Authentication is handled by the auth.py module...",
  "sources": [
    {
      "id": "doc-1",
      "title": "auth.py",
      "snippet": "def authenticate_user(username, password)..."
    }
  ],
  "agent_used": "document",
  "confidence": 0.92,
  "metadata": {
    "code_blocks": [
      {
        "language": "python",
        "code": "def authenticate_user()...",
        "index": 0
      }
    ],
    "has_code": true
  }
}
```

### 💾 **Conversations**

```bash
# List all conversations
GET /conversations?limit=50

# Get conversation history
GET /conversations/{session_id}

# Search conversations
GET /conversations/search?q=authentication

# Delete conversation
DELETE /conversations/{session_id}

# Export conversation
GET /conversations/{session_id}/export?format=markdown

# Get summary
GET /conversations/{session_id}/summary
```

### ⚙️ **Settings**

```bash
# Get current settings
GET /settings

# Update LLM settings
POST /settings/llm
{
  "model": "gpt-4",
  "temperature": 0.5,
  "max_tokens": 2000
}

# Get available models
GET /models
```

### 📊 **System**

```bash
# Health check
GET /health

# System status
GET /status
```

## 🎯 Use Cases

### 1. **Codebase Onboarding**
New developer joins? Index the repo and let them ask questions:

```bash
# Index repository
curl -X POST http://localhost:8000/ingest/github \
  -d "repo_url=https://github.com/company/backend"

# Ask questions
curl -X POST http://localhost:8000/query \
  -d '{"query": "How do I add a new API endpoint?"}'
```

### 2. **Technical Documentation Search**
Upload docs and search with natural language:

```bash
# Upload documentation
curl -X POST http://localhost:8000/ingest \
  -F "file=@api-docs.pdf"

# Search with filters
curl -X POST http://localhost:8000/query \
  -d '{"query": "authentication flow", "filters": {"tags": "api"}}'
```

### 3. **Code Review Assistant**
Find patterns, bugs, or inconsistencies:

```bash
# Index local project
curl -X POST http://localhost:8000/ingest/local \
  -d "directory_path=/home/user/myproject"

# Ask code questions
curl -X POST http://localhost:8000/query \
  -d '{"query": "Find all database queries without prepared statements"}'
```

### 4. **Debug Helper**
Save past bug fixes and search them:

```bash
# Index bug reports and fixes
curl -X POST http://localhost:8000/ingest/local \
  -d "directory_path=/home/user/bug-fixes"

# Search for similar issues
curl -X POST http://localhost:8000/query \
  -d '{"query": "TypeError: Cannot read property of undefined"}'
```

## 💻 Frontend Pages

### 🏠 **Homepage**
- Vibrant gradient (indigo → purple → pink)
- 4 feature cards with emoji
- Quick start guide with 3 steps
- Ready-to-use example questions

### 💬 **Chat Page**
- Robot emoji 🤖 for AI responses
- User emoji 👤 for questions
- Clickable example questions
- Code syntax highlighting
- Source citations with snippets
- Gradient message bubbles

### 📄 **Documents Page**
- Drag & drop upload area
- File type validation
- Upload progress
- Batch processing support
- 3-step how-it-works guide

### 📊 **Dashboard Page**
- Real-time statistics
- Total documents count
- Queries today counter
- System uptime display
- Mock/Live mode indicator
- Quick action cards

## 🔐 Security

- ✅ API keys in environment variables
- ✅ SQLite with parameterized queries
- ✅ File type validation
- ✅ Size limits (500KB per file)
- ✅ CORS configured for localhost
- ✅ No sensitive data logging

## 📊 Performance

| Metric | Value |
|--------|-------|
| **Vector Search** | ChromaDB with embeddings |
| **Response Time** | ~2-3s for RAG queries |
| **Concurrency** | 100+ concurrent requests |
| **Storage** | SQLite + ChromaDB |
| **Memory** | ~500MB + vector DB size |
| **Supported Files** | 20+ file types |
| **Max File Size** | 500KB (configurable) |

## 🛠️ Development

### Mock Mode (No API Key)
```bash
# In .env
USE_MOCK_LLM=true
```

### Environment Variables
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...          # Your API key
USE_MOCK_LLM=false             # Enable mock mode
LLM_MODEL=gpt-3.5-turbo        # Model selection
LLM_TEMPERATURE=0.7            # Creativity (0.0-2.0)
LLM_MAX_TOKENS=1000            # Max response length
LLM_STREAMING=false            # Enable streaming

# Server Configuration
PYTHON_AGENT_PORT=8000         # Backend port
NEXT_PUBLIC_API_BASE_URL=http://localhost:3000
```

### Supported File Types
```
Code: .py .js .ts .jsx .tsx .java .cpp .c .h .go .rs .rb .php .cs .swift .kt .scala
Docs: .md .txt .json .yaml .yml .toml .xml
```

### Ignored Directories
```
node_modules, .git, __pycache__, venv, env, dist, build, target, .next, .cache, coverage
```

## 📈 Statistics

### Backend API
- **Lines of Code**: 460+ (app.py alone)
- **Endpoints**: 20+ REST endpoints
- **Features**: 8 major new features
- **Database**: SQLite + ChromaDB
- **Models**: Supports 4 GPT models

### Frontend UI
- **Pages**: 4 fully redesigned pages
- **Components**: 20+ React components
- **Styling**: Tailwind CSS with gradients
- **Icons**: Lucide React icons
- **Framework**: Next.js 14 + TypeScript

## 🎓 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **LangChain** - RAG orchestration
- **ChromaDB** - Vector database
- **SQLite** - Conversation storage
- **Pydantic** - Data validation
- **OpenAI** - LLM provider

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Hooks** - State management
- **Lucide Icons** - Beautiful icons

## 📝 License

MIT License - Free for commercial use!

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📧 Contact

- **GitHub**: https://github.com/Aryam2121/CodeMind
- **Issues**: https://github.com/Aryam2121/CodeMind/issues
- **Email**: support@codemind.dev

## 🌟 Star History

If you find CodeMind useful, please give it a ⭐ on GitHub!

---

**Built with ❤️ by Aryaman, for developers**

*Powered by RAG • LangChain • OpenAI • FastAPI • Next.js*
