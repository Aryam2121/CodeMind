# Architecture Overview - Smart City AI Assistant

## 🏗️ System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                     (Browser - Port 3000)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS/REST
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    NEXT.JS FRONTEND                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Pages:                                                   │  │
│  │  • Home (/)           - Landing page                     │  │
│  │  • Chat (/chat)       - AI conversation interface        │  │
│  │  • Map (/map)         - Geo-spatial visualization        │  │
│  │  • Documents (/docs)  - Upload & manage documents        │  │
│  │  • Dashboard (/dash)  - Admin metrics & monitoring       │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Routes (/api):                                       │  │
│  │  • /api/ai/query      - Proxy to Python agent            │  │
│  │  • /api/ai/upload     - Document ingestion proxy         │  │
│  │  • /api/ai/status     - System status proxy              │  │
│  │  • /api/complaints    - Geo-data endpoint                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              PYTHON AGENT SERVICE (FastAPI)                      │
│                      (Port 8000)                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  REST Endpoints:                                          │  │
│  │  • POST /ingest       - Document ingestion                │  │
│  │  • POST /query        - Natural language queries          │  │
│  │  • GET  /status       - Health & statistics               │  │
│  │  • GET  /health       - Simple health check               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│  ┌──────────────────────────▼────────────────────────────────┐  │
│  │           AGENT ORCHESTRATOR (MCP Pattern)                │  │
│  │                                                            │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │  │
│  │  │ Document   │  │    GIS     │  │  Summary   │         │  │
│  │  │   Agent    │  │   Agent    │  │   Agent    │  ...    │  │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘         │  │
│  │        │                │                │                 │  │
│  │        └────────────────┴────────────────┘                 │  │
│  │                         │                                   │  │
│  └─────────────────────────┼───────────────────────────────┘  │
│                             │                                   │
│  ┌─────────────────────────▼───────────────────────────────┐  │
│  │              RAG PIPELINE (LangChain)                    │  │
│  │                                                           │  │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐          │  │
│  │  │Retriever │───▶│Embeddings│───▶│   LLM    │          │  │
│  │  │ (Top-K)  │    │(OpenAI/  │    │(GPT-3.5/ │          │  │
│  │  │          │    │ Mock)    │    │  Mock)   │          │  │
│  │  └────┬─────┘    └──────────┘    └──────────┘          │  │
│  │       │                                                   │  │
│  └───────┼───────────────────────────────────────────────┘  │
│          │                                                    │
│  ┌───────▼────────────────────────────────────────────────┐  │
│  │              DOCUMENT INGESTION                         │  │
│  │                                                          │  │
│  │  PDF Parser → Text Splitter → Chunk Generator          │  │
│  │  DOCX Parser→ Metadata Enrichment → Vector Embeddings  │  │
│  │  TXT Parser → Quality Checks                            │  │
│  └──────────────────────────┬───────────────────────────┘  │
└─────────────────────────────┼──────────────────────────────┘
                              │
                              │ Store/Retrieve
                              │
┌─────────────────────────────▼──────────────────────────────────┐
│                    DATA STORAGE LAYER                           │
│                                                                  │
│  ┌─────────────────────┐    ┌─────────────────────────────┐   │
│  │  CHROMA VECTOR DB   │    │   FILE SYSTEM / CSV         │   │
│  │                     │    │                             │   │
│  │  • Document chunks  │    │  • Complaints data          │   │
│  │  • Embeddings       │    │  • Original documents       │   │
│  │  • Metadata         │    │  • Logs                     │   │
│  │  • Similarity index │    │                             │   │
│  └─────────────────────┘    └─────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

## 🔄 Request Flow Diagrams

### Chat Query Flow
```
User Types Query in Browser
          │
          ▼
Frontend /chat Page (React)
          │
          │ POST /api/ai/query
          ▼
Next.js API Route
          │
          │ Forward to Python Agent
          │ POST http://localhost:8000/query
          ▼
FastAPI /query Endpoint
          │
          ▼
Agent Orchestrator
          │
          ├─▶ Analyze Query Intent
          │   • Keywords detection
          │   • Pattern matching
          │   • Context analysis
          │
          ▼
Route to Appropriate Agent
          │
          ├─▶ DocumentAgent?   (policy, SOP keywords)
          ├─▶ GISAgent?        (ward, location keywords)
          ├─▶ SummaryAgent?    (summarize, overview keywords)
          └─▶ ComplianceAgent? (compliant, regulation keywords)
          │
          ▼
Selected Agent.process()
          │
          ▼
RAG Pipeline
          │
          ├─▶ 1. Embed Query (OpenAI Embeddings)
          │
          ├─▶ 2. Vector Search (Chroma DB)
          │      • Similarity search
          │      • Filter by metadata
          │      • Get top_k results
          │
          ├─▶ 3. Format Context
          │      • Combine chunks
          │      • Add source info
          │      • Prepare prompt
          │
          └─▶ 4. Generate Answer (LLM)
                 • Send to OpenAI/Mock
                 • Parse response
                 • Extract citations
          │
          ▼
Create Response Object
          │
          ├─▶ answer: string
          ├─▶ sources: [...]
          ├─▶ agent_used: string
          ├─▶ confidence: float
          └─▶ fallback: boolean
          │
          ▼
Return JSON to Frontend
          │
          ▼
Display in Chat UI
          │
          ├─▶ Message bubble
          ├─▶ Source citations
          └─▶ Agent indicator
```

### Document Upload Flow
```
User Selects File
          │
          ▼
Frontend /documents Page
          │
          │ FormData with file
          ▼
POST /api/ai/upload
          │
          ▼
Forward to Python Agent
POST /ingest
          │
          ▼
Document Ingester
          │
          ├─▶ 1. Validate File
          │      • Check format (PDF/DOCX/TXT)
          │      • Check size
          │
          ├─▶ 2. Extract Text
          │      • PyPDF for PDFs
          │      • python-docx for DOCX
          │      • Direct read for TXT
          │
          ├─▶ 3. Split into Chunks
          │      • RecursiveCharacterTextSplitter
          │      • chunk_size: 1000
          │      • chunk_overlap: 200
          │
          ├─▶ 4. Generate Embeddings
          │      • Each chunk → vector
          │      • OpenAI text-embedding-ada-002
          │
          ├─▶ 5. Store in Vector DB
          │      • Chroma.add_documents()
          │      • Persist to disk
          │      • Index for search
          │
          └─▶ 6. Return IDs
                 • List of chunk IDs
                 • Metadata
          │
          ▼
Success Response
          │
          ▼
Update UI
          │
          └─▶ Show success message
              "Uploaded! 12 chunks indexed"
```

### Map Visualization Flow
```
User Opens /map Page
          │
          ▼
Frontend Map Component
          │
          │ GET /api/complaints
          ▼
Next.js API Route
          │
          ├─▶ Read complaints.csv
          │   or Return Mock Data
          │
          ▼
Parse CSV Data
          │
          ├─▶ Extract fields:
          │   • id, lat, lon
          │   • type, ward, date
          │   • description, status
          │
          ▼
Return JSON Array
          │
          ▼
React-Leaflet Map
          │
          ├─▶ Initialize map
          │   • Center: [12.97, 77.59]
          │   • Zoom: 13
          │
          ├─▶ Add markers
          │   • For each complaint
          │   • Position: [lat, lon]
          │
          ├─▶ Add popups
          │   • Complaint details
          │   • Type, ward, status
          │
          └─▶ Add filters
              • Ward dropdown
              • Type dropdown
          │
          ▼
User Interacts
          │
          ├─▶ Click marker → Show popup
          ├─▶ Change filter → Re-render
          └─▶ Pan/zoom → Update view
```

## 🧩 Component Responsibilities

### Frontend Components

#### ChatBox (`/app/chat/page.tsx`)
- **Purpose**: AI conversation interface
- **Features**:
  - Message history
  - Real-time responses
  - Source citations
  - Loading states
- **State**: messages[], input, isLoading
- **API Calls**: POST /api/ai/query

#### MapPanel (`/app/map/page.tsx`)
- **Purpose**: Geo-spatial visualization
- **Features**:
  - Interactive Leaflet map
  - Complaint markers
  - Filtering (ward, type)
  - Statistics display
- **State**: complaints[], filters
- **API Calls**: GET /api/complaints

#### UploadDocs (`/app/documents/page.tsx`)
- **Purpose**: Document management
- **Features**:
  - File upload (drag-drop)
  - Progress indication
  - Success/error handling
- **State**: file, uploading, result
- **API Calls**: POST /api/ai/upload

#### Dashboard (`/app/dashboard/page.tsx`)
- **Purpose**: System monitoring
- **Features**:
  - Real-time statistics
  - Health indicators
  - Quick actions
  - Auto-refresh
- **State**: stats, isLoading
- **API Calls**: GET /api/ai/status

### Backend Modules

#### AgentOrchestrator (`agents.py`)
- **Purpose**: Route queries to specialized agents
- **Logic**:
  1. Analyze query for keywords
  2. Match to agent capabilities
  3. Invoke selected agent
  4. Return unified response
- **Agents**: Document, GIS, Summary, Compliance

#### RAGPipeline (`rag.py`)
- **Purpose**: Retrieval-Augmented Generation
- **Process**:
  1. Embed query
  2. Search vector DB
  3. Format context
  4. Generate answer
  5. Create citations
- **Dependencies**: LangChain, OpenAI, Chroma

#### DocumentIngester (`ingest.py`)
- **Purpose**: Parse and index documents
- **Supported**: PDF, DOCX, TXT
- **Process**:
  1. Parse file
  2. Extract text
  3. Split into chunks
  4. Generate embeddings
  5. Store in vector DB

#### VectorStore (`vector_store.py`)
- **Purpose**: Vector database interface
- **Operations**:
  - add_documents()
  - similarity_search()
  - get_stats()
- **Backend**: Chroma DB

## 🔐 Security Considerations

### API Key Management
- Stored in `.env` file (not committed)
- Accessed via environment variables
- Never exposed to frontend

### CORS Configuration
- Allowed origins: localhost:3000
- Credentials enabled
- Secure headers

### Input Validation
- File type checking
- Size limits
- Query sanitization
- Metadata validation

### Error Handling
- No sensitive data in errors
- Generic error messages to users
- Detailed logs server-side

## 📊 Data Flow

### Write Path (Ingestion)
```
File Upload → Parse → Chunk → Embed → Store → Index
```

### Read Path (Query)
```
User Query → Embed → Search → Retrieve → Generate → Display
```

## 🚀 Scalability Considerations

### Current Capacity
- **Concurrent Users**: 10-50
- **Documents**: 1,000-10,000
- **Query Latency**: 2-5 seconds
- **Storage**: Local file system

### Scaling Options
1. **Horizontal Scaling**
   - Load balancer
   - Multiple agent instances
   - Shared vector DB

2. **Caching**
   - Redis for frequent queries
   - CDN for static assets
   - Query result caching

3. **Database**
   - Cloud vector DB (Pinecone, Weaviate)
   - Dedicated PostgreSQL
   - Object storage (S3)

## 🎯 Performance Optimization

### Frontend
- Code splitting
- Lazy loading
- Image optimization
- Bundle size reduction

### Backend
- Connection pooling
- Batch processing
- Async operations
- Response compression

### Vector DB
- Index optimization
- Query result caching
- Metadata filtering
- Batch embeddings

---

**This architecture provides a solid foundation for a production-ready Smart City AI Assistant with room for growth and optimization.**
