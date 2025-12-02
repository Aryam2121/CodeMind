# 🚀 Startup Checklist - Smart City AI Assistant

Use this checklist to ensure everything is configured correctly before starting the application.

## ☑️ Pre-Flight Checklist

### System Requirements
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Python 3.9+ installed (`python --version`)
- [ ] npm 9+ installed (`npm --version`)
- [ ] pip installed (`pip --version`)
- [ ] Git installed (optional)
- [ ] Docker installed (optional, for containerized deployment)

### Project Setup
- [ ] Repository cloned/downloaded
- [ ] Located in project root directory (`cd AI-Agent`)
- [ ] `.env` file created from `.env.example`
- [ ] Environment variables configured (see below)

### Environment Configuration

#### Option 1: Mock Mode (No API Key Required)
```
✓ USE_MOCK_LLM=true
✓ CHROMA_DB_DIR=./chroma_db
✓ PYTHON_AGENT_PORT=8000
✓ PORT=3000
```

#### Option 2: Production Mode (OpenAI API)
```
✓ OPENAI_API_KEY=sk-your-actual-key
✓ USE_MOCK_LLM=false
✓ LLM_MODEL=gpt-3.5-turbo
✓ EMBEDDING_MODEL=text-embedding-ada-002
✓ CHROMA_DB_DIR=./chroma_db
✓ PYTHON_AGENT_PORT=8000
✓ PORT=3000
```

### Dependencies Installation

#### Root Dependencies
```bash
cd AI-Agent
npm install
```
- [ ] Root packages installed successfully

#### Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```
- [ ] Frontend packages installed successfully
- [ ] No dependency conflicts
- [ ] No peer dependency warnings (critical)

#### Python Agent Dependencies
```bash
cd python-agent
pip install -r requirements.txt
cd ..
```
- [ ] Python packages installed successfully
- [ ] PyPDF installed
- [ ] python-docx installed
- [ ] chromadb installed
- [ ] langchain installed
- [ ] fastapi installed

### Port Availability
- [ ] Port 3000 available for frontend
- [ ] Port 8000 available for Python agent

Check with:
```bash
# Windows
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :3000
lsof -i :8000
```

## 🏃 Startup Sequence

### Local Development Mode

#### Step 1: Start Python Agent
```bash
cd python-agent
python app.py
```

**Expected Output:**
```
INFO: Starting Smart City AI Agent service...
INFO: All services initialized successfully
INFO: Uvicorn running on http://0.0.0.0:8000
```

**Verify:**
- [ ] Server starts without errors
- [ ] Logs show "All services initialized successfully"
- [ ] Can access http://localhost:8000/docs

**Quick Test:**
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok","timestamp":"..."}
```

#### Step 2: Start Frontend (New Terminal)
```bash
cd frontend
npm run dev
```

**Expected Output:**
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

**Verify:**
- [ ] Server starts without errors
- [ ] No compilation errors
- [ ] Can access http://localhost:3000

#### Step 3: Load Test Data (New Terminal)
```bash
# Windows
scripts\test-data-load.bat

# Linux/Mac
chmod +x scripts/test-data-load.sh
./scripts/test-data-load.sh
```

**Verify:**
- [ ] Documents uploaded successfully
- [ ] See ingestion confirmation messages
- [ ] No errors in Python agent logs

### Docker Mode

#### Step 1: Configure Environment
- [ ] `.env` file exists with correct values
- [ ] Docker is running

#### Step 2: Build Images
```bash
docker-compose -f infra/docker-compose.yml build
```

**Verify:**
- [ ] Both images build successfully
- [ ] No build errors

#### Step 3: Start Services
```bash
docker-compose -f infra/docker-compose.yml up -d
```

**Verify:**
- [ ] Both containers start successfully
- [ ] Containers are healthy

```bash
docker-compose -f infra/docker-compose.yml ps
```

## ✅ Verification Tests

### 1. Python Agent Health Check
```bash
curl http://localhost:8000/health
```
**Expected:** `{"status":"ok",...}`
- [ ] Returns 200 OK
- [ ] JSON response received

### 2. Agent Status Check
```bash
curl http://localhost:8000/status
```
**Expected:** Stats object with documents, queries, etc.
- [ ] Returns 200 OK
- [ ] Shows system statistics

### 3. Frontend Homepage
**Navigate to:** http://localhost:3000

**Verify:**
- [ ] Page loads successfully
- [ ] See 4 feature cards
- [ ] No JavaScript errors in console
- [ ] Styling looks correct

### 4. Chat Interface
**Navigate to:** http://localhost:3000/chat

**Test Query:** "What is the timeline for pothole repairs?"

**Verify:**
- [ ] Can type in input field
- [ ] Send button works
- [ ] Receives AI response
- [ ] Response shows within 5 seconds
- [ ] Source citations displayed (if documents loaded)

### 5. Map View
**Navigate to:** http://localhost:3000/map

**Verify:**
- [ ] Map loads and displays
- [ ] See complaint markers
- [ ] Can click on markers
- [ ] Filters work (Ward, Type)
- [ ] Statistics update when filtering

### 6. Document Upload
**Navigate to:** http://localhost:3000/documents

**Test:** Upload `test-data/documents/water-supply-sop.txt`

**Verify:**
- [ ] File selection works
- [ ] Upload button appears
- [ ] Upload completes successfully
- [ ] Success message shows number of chunks

### 7. Dashboard
**Navigate to:** http://localhost:3000/dashboard

**Verify:**
- [ ] Statistics cards display
- [ ] Shows correct document count
- [ ] System info table visible
- [ ] Status indicator shows correct mode

### 8. API Integration Test
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"test query\",\"top_k\":4}"
```

**Verify:**
- [ ] Returns 200 OK
- [ ] Response includes "answer" field
- [ ] Response includes "sources" array
- [ ] Response includes "agent_used" field

## 🐛 Troubleshooting Quick Reference

### Python Agent Won't Start
```bash
# Check Python version
python --version  # Need 3.9+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check port
netstat -ano | findstr :8000
```

### Frontend Won't Start
```bash
# Clear cache
cd frontend
rd /s /q .next node_modules
npm install
npm run dev
```

### No Response from AI
1. Check Python agent is running: `curl http://localhost:8000/health`
2. Check `PYTHON_AGENT_URL` in `.env`
3. Check browser console for errors
4. Verify API route: `curl http://localhost:3000/api/ai/status`

### Documents Not Loading
1. Verify test data exists: `dir test-data\documents`
2. Check Python agent logs for errors
3. Verify Chroma DB directory: `dir chroma_db`
4. Try re-running test data load script

### Map Not Showing
1. Check browser console for Leaflet errors
2. Verify complaints API: `curl http://localhost:3000/api/complaints`
3. Check if test-data/complaints.csv exists
4. Disable browser ad blockers

## 📞 Support Checklist

If you need to ask for help, gather this information:

- [ ] Operating System and version
- [ ] Node.js version
- [ ] Python version
- [ ] Error messages (full text)
- [ ] Console logs (frontend)
- [ ] Server logs (Python agent)
- [ ] Steps to reproduce
- [ ] Environment variables (redact API key!)

## 🎉 Success Criteria

You're ready to go when:

✅ Python agent running on port 8000
✅ Frontend running on port 3000
✅ Health checks pass
✅ Can ask questions in chat
✅ Map displays complaints
✅ Can upload documents
✅ Dashboard shows statistics
✅ No errors in logs

---

**🚀 Happy Building!**

If all checks pass, you're ready to start developing or using the Smart City AI Assistant!
