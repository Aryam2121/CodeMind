# Quick Start Guide - Smart City AI Assistant

## 🚀 Get Started in 5 Minutes

### Option 1: Local Development (Recommended for Development)

#### Step 1: Install Prerequisites
```bash
# Check Node.js (need 18+)
node --version

# Check Python (need 3.9+)
python --version

# Install dependencies
npm install
cd frontend && npm install && cd ..
cd python-agent && pip install -r requirements.txt && cd ..
```

#### Step 2: Configure Environment
```bash
# Copy environment template
copy .env.example .env

# Edit .env file - Option A: Use Mock Mode (no API key needed)
# Set: USE_MOCK_LLM=true

# Or Option B: Use Real OpenAI
# Set: OPENAI_API_KEY=sk-your-key-here
```

#### Step 3: Start Services
```bash
# Terminal 1: Start Python Agent
cd python-agent
python app.py

# Terminal 2: Start Frontend (new terminal)
cd frontend
npm run dev
```

#### Step 4: Load Test Data
```bash
# Terminal 3: Load sample documents (new terminal)
scripts\test-data-load.bat
```

#### Step 5: Access the Application
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Agent Status**: http://localhost:8000/status

---

### Option 2: Docker (Recommended for Production)

#### Step 1: Configure Environment
```bash
copy .env.example .env
# Edit .env with your settings
```

#### Step 2: Start with Docker Compose
```bash
# Build and start all services
docker-compose -f infra/docker-compose.yml up -d

# View logs
docker-compose -f infra/docker-compose.yml logs -f

# Check status
docker-compose -f infra/docker-compose.yml ps
```

#### Step 3: Access the Application
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

#### Stop Services
```bash
docker-compose -f infra/docker-compose.yml down
```

---

## 📝 Try Example Queries

### In the Chat Interface (http://localhost:3000/chat)

1. **Document Query**
   ```
   What are the water quality testing requirements?
   ```

2. **Geo-spatial Query**
   ```
   Show pothole complaints in Ward 12 in the last 30 days
   ```

3. **Compliance Query**
   ```
   Is delaying pothole repair beyond 15 days compliant with SOP?
   ```

4. **Summary Query**
   ```
   Summarize the road maintenance procedures
   ```

---

## 🗺️ Explore the Map

1. Go to http://localhost:3000/map
2. Use filters to view complaints by:
   - Ward (11, 12, 13)
   - Type (Pothole, Water Supply, Street Light, etc.)
3. Click markers to see complaint details

---

## 📤 Upload Documents

1. Go to http://localhost:3000/documents
2. Click "Choose a file" or drag & drop
3. Select a PDF, DOCX, or TXT file
4. Click "Upload"
5. Document is automatically indexed and searchable!

---

## 📊 View Dashboard

1. Go to http://localhost:3000/dashboard
2. See real-time statistics:
   - Total documents in knowledge base
   - Queries processed today
   - System uptime
   - LLM mode (Mock or Live)

---

## 🧪 Test the API Directly

### Check Status
```bash
curl http://localhost:8000/status
```

### Query AI
```bash
curl -X POST http://localhost:8000/query ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"What is the timeline for pothole repairs?\",\"top_k\":4}"
```

### Upload Document
```bash
curl -X POST http://localhost:8000/ingest ^
  -F "file=@test-data/documents/water-supply-sop.txt" ^
  -F "metadata={\"source_name\":\"Water SOP\"}"
```

---

## ⚙️ Configuration Options

### Mock vs Real LLM

**Mock Mode (Development)**
```env
USE_MOCK_LLM=true
# No API key needed
# Fast responses
# Template-based answers
```

**Real Mode (Production)**
```env
USE_MOCK_LLM=false
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-3.5-turbo
# Accurate AI responses
# Requires API key
# Costs per query
```

### Vector Database
```env
CHROMA_DB_DIR=./chroma_db
# Persistent storage for indexed documents
# Automatically created on first run
```

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Windows: Kill process on port
netstat -ano | findstr :3000
taskkill /PID <process_id> /F

# Or change port in .env
PORT=3001
```

### Python Agent Won't Start
```bash
# Check dependencies
cd python-agent
pip install -r requirements.txt

# Check port
netstat -ano | findstr :8000
```

### Frontend Build Errors
```bash
cd frontend
# Clear cache
del /s /q .next node_modules
npm install
npm run dev
```

### Docker Issues
```bash
# Reset everything
docker-compose -f infra/docker-compose.yml down -v
docker-compose -f infra/docker-compose.yml build --no-cache
docker-compose -f infra/docker-compose.yml up
```

---

## 📚 Next Steps

1. **Read Full Documentation**: [README.md](README.md)
2. **Explore Agents**: [agents.py](python-agent/agents.py)
3. **Customize RAG Pipeline**: [rag.py](python-agent/rag.py)
4. **Add Your Documents**: Upload PDFs/DOCX via UI
5. **Customize Frontend**: [frontend/app/](frontend/app/)

---

## 🤝 Need Help?

- **Documentation**: See [README.md](README.md)
- **API Reference**: http://localhost:8000/docs
- **Demo**: See [demo-recording.md](demo-recording.md)
- **Issues**: https://github.com/yourusername/AI-Agent/issues

---

## 🎉 Success!

You now have a fully functional Smart City AI Assistant running locally!

**What You Can Do:**
✅ Ask questions about policies and SOPs
✅ Visualize complaints on an interactive map
✅ Upload and index new documents
✅ Get AI-powered answers with citations
✅ Filter and analyze geo-spatial data
✅ Check compliance with regulations
✅ Monitor system health and statistics

**Enjoy building smart city solutions! 🏙️**
