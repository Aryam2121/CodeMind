# Smart City Unified AI Knowledge Assistant

A production-ready, end-to-end AI system combining Multi-Agent orchestration (MCP pattern), Retrieval-Augmented Generation (RAG), and interactive map visualization for smart city management.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Chat UI  │  │ Map Panel│  │ Doc Upload│  │Dashboard │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │              │             │           │
│       └─────────────┴──────────────┴─────────────┘           │
│                          │                                    │
│                    API Routes (/api/ai/*)                    │
└──────────────────────────┼────────────────────────────────────┘
                           │ HTTP/REST
┌──────────────────────────┼────────────────────────────────────┐
│              Python Agent Service (FastAPI)                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Agent Orchestrator (MCP)                  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │Document  │ │   GIS    │ │ Summary  │ │Compliance│ │  │
│  │  │  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │ │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │  │
│  └───────┼────────────┼────────────┼────────────┼────────┘  │
│          │            │            │            │            │
│  ┌───────▼────────────▼────────────▼────────────▼────────┐  │
│  │              RAG Pipeline (LangChain)                  │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │  │
│  │  │ Retriever│  │Embeddings│  │   LLM    │            │  │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘            │  │
│  └───────┼─────────────┼─────────────┼────────────────────┘  │
│          │             │             │                        │
│  ┌───────▼─────────────▼─────────────▼────────────────────┐  │
│  │              Vector Store (Chroma)                      │  │
│  │        + Document Store + Geo Complaints DB            │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

## ✨ Features

### Core Capabilities
- **Multi-Agent Orchestration**: Specialized agents (Document, GIS, Summary, Compliance) handle different query types
- **Retrieval-Augmented Generation**: Context-aware responses with source citations
- **Vector Search**: Fast semantic search over government documents using Chroma DB
- **Geo-spatial Analysis**: Map visualization of complaints, potholes, and incidents
- **Document Processing**: Ingestion of PDFs, DOCX, and text files with metadata

### User Interface
- **Interactive Chat**: Natural language queries with streaming responses
- **Live Map**: Filter and visualize geo-tagged issues by ward, date, type
- **Document Management**: Upload, search, and view source documents
- **Admin Dashboard**: Real-time metrics on documents, queries, and system health

### Developer Experience
- **One-Command Setup**: `npm install && npm run dev`
- **Docker Support**: Full containerization with docker-compose
- **Mock Mode**: Development without API keys using template responses
- **Comprehensive Tests**: Unit and integration tests for all components
- **CI/CD Ready**: GitHub Actions for automated testing and deployment

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm 9+
- **Python** 3.9+ with pip
- **Docker** (optional, for containerized deployment)

### Local Development

1. **Clone and Install**
   ```bash
   git clone <repository-url>
   cd AI-Agent
   npm install
   cd frontend && npm install && cd ..
   cd python-agent && pip install -r requirements.txt && cd ..
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   # Or set USE_MOCK_LLM=true for development
   ```

3. **Load Test Data**
   ```bash
   # Windows
   scripts\test-data-load.bat
   
   # Linux/Mac
   chmod +x scripts/test-data-load.sh
   ./scripts/test-data-load.sh
   ```

4. **Start Development Servers**
   ```bash
   npm run dev
   ```
   
   This starts:
   - Frontend: http://localhost:3000
   - Python Agent: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Docker Deployment

```bash
# Build and start all services
npm run docker:build
npm run docker:up

# Stop services
npm run docker:down
```

## 📊 Example Queries

Try these queries in the Chat UI:

1. **Geo-spatial Query**
   ```
   Show pothole complaints in Ward 12 in the last 30 days and summarize SOP to resolve them.
   ```

2. **Document Analysis**
   ```
   Extract action items from circular 'water-supply-update.pdf' pages 4-6.
   ```

3. **Comparative Analysis**
   ```
   Compare water complaints this month vs last month and suggest priority wards.
   ```

4. **Compliance Check**
   ```
   Is delaying road repairs beyond 15 days compliant with SOP-2024-03?
   ```

## 🔌 API Reference

### Python Agent Endpoints

#### POST /ingest
Ingest documents into the vector store.

**Request:**
```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@document.pdf" \
  -F 'metadata={"source_name":"Water Policy 2024","uploaded_by":"admin"}'
```

**Response:**
```json
{
  "status": "ok",
  "ingested": 45,
  "ids": ["doc_uuid_1", "doc_uuid_2", ...],
  "metadata": {
    "total_chunks": 45,
    "source": "document.pdf"
  }
}
```

#### POST /query
Query the knowledge base with natural language.

**Request:**
```json
{
  "query": "What are the water quality standards?",
  "top_k": 4,
  "agents": ["document", "compliance"]
}
```

**Response:**
```json
{
  "answer": "According to the Water Quality Standards 2024...",
  "sources": [
    {
      "id": "doc_uuid_1",
      "title": "water-policy-2024.pdf",
      "page": 12,
      "snippet": "Water quality must meet WHO standards..."
    }
  ],
  "agent_used": "document",
  "confidence": 0.89,
  "fallback": false
}
```

#### GET /status
Check service health and statistics.

**Response:**
```json
{
  "status": "healthy",
  "stats": {
    "documents": 234,
    "vectors": 12450,
    "queries_today": 89
  },
  "version": "1.0.0"
}
```

### Frontend API Routes

#### POST /api/ai/query
Proxy to Python agent with rate limiting.

#### POST /api/ai/upload
Upload documents with authentication.

#### GET /api/complaints
Fetch geo-tagged complaints for map visualization.

## 🧪 Testing

```bash
# Run all tests
npm test

# Frontend tests only (Jest)
npm run test:frontend

# Python agent tests (pytest)
npm run test:agent

# With coverage
cd python-agent && pytest --cov=. --cov-report=html
```

## 🏗️ Project Structure

```
AI-Agent/
├── frontend/                 # Next.js application
│   ├── app/                 # App router (Next.js 13+)
│   │   ├── api/            # API routes
│   │   │   └── ai/         # AI endpoints
│   │   ├── chat/           # Chat page
│   │   ├── map/            # Map visualization
│   │   └── dashboard/      # Admin dashboard
│   ├── components/          # React components
│   │   ├── ChatBox.tsx
│   │   ├── MapPanel.tsx
│   │   ├── UploadDocs.tsx
│   │   └── Dashboard.tsx
│   └── lib/                # Utilities and types
│
├── python-agent/            # LangChain + FastAPI service
│   ├── app.py              # FastAPI application
│   ├── agents.py           # Multi-agent orchestration
│   ├── ingest.py           # Document ingestion
│   ├── rag.py              # RAG pipeline
│   ├── vector_store.py     # Chroma interface
│   ├── models.py           # Pydantic models
│   └── tests/              # Python tests
│
├── infra/                   # Infrastructure
│   ├── docker-compose.yml
│   ├── Dockerfile.frontend
│   └── Dockerfile.agent
│
├── scripts/                 # Utility scripts
│   ├── start-local.sh
│   ├── test-data-load.sh
│   └── reindex.sh
│
├── test-data/              # Sample data
│   ├── documents/          # Sample PDFs
│   └── complaints.csv      # Geo-tagged complaints
│
└── tests/                  # Integration tests
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Yes* | - |
| `USE_MOCK_LLM` | Use mock responses | No | false |
| `CHROMA_DB_DIR` | Vector DB directory | No | ./chroma_db |
| `PYTHON_AGENT_PORT` | Agent service port | No | 8000 |
| `NEXT_PUBLIC_MAPBOX_TOKEN` | Mapbox token | No | - |

*Required unless `USE_MOCK_LLM=true`

### LLM Providers

**OpenAI (Default)**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-3.5-turbo
```

**Mock Mode (Development)**
```bash
USE_MOCK_LLM=true
```

**Local LLM (Advanced)**
```bash
LLM_PROVIDER=local
LLM_MODEL=llama2
LLM_API_BASE=http://localhost:11434
```

## 🤖 Extending Agents

To add a new agent:

1. Create agent class in `python-agent/agents.py`:
```python
class TrafficAgent(BaseAgent):
    def can_handle(self, query: str) -> bool:
        return any(keyword in query.lower() 
                   for keyword in ['traffic', 'congestion', 'signal'])
    
    async def process(self, query: str, context: dict) -> AgentResponse:
        # Your agent logic
        pass
```

2. Register in `AgentOrchestrator`:
```python
self.agents.append(TrafficAgent())
```

## 🐛 Troubleshooting

**Issue**: Vector DB initialization fails
```bash
# Clear and reinitialize
rm -rf chroma_db/
python python-agent/vector_store.py --init
```

**Issue**: Frontend can't connect to backend
- Check `PYTHON_AGENT_URL` in `.env`
- Ensure Python agent is running on port 8000
- Check firewall/CORS settings

**Issue**: Mock LLM not working
- Set `USE_MOCK_LLM=true` in `.env`
- Restart Python agent service

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Commit Message Convention
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions/changes
- `chore:` Maintenance tasks

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- LangChain for RAG framework
- Chroma for vector database
- Next.js and Vercel team
- OpenAI for embeddings and LLM API

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: [Wiki](wiki)
- **Discussions**: GitHub Discussions

---

Built with ❤️ for Smart Cities
