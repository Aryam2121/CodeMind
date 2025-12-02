# 🏗️ Universal AI Workspace - Architecture

## Overview

The Universal AI Workspace is built on a modern, scalable architecture that combines cutting-edge AI technologies with robust software engineering practices.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                           │
│              (Next.js 14 + React + Tailwind)                 │
└──────────────────┬──────────────────────────────────────────┘
                   │ REST API / WebSocket
┌──────────────────▼──────────────────────────────────────────┐
│                  API Gateway                                 │
│              (FastAPI + Python)                              │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
│  │    Auth    │ │   Router   │ │  WebSocket │              │
│  └────────────┘ └────────────┘ └────────────┘              │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│           LangChain Orchestration Layer                      │
│  ┌──────────────────────────────────────────────────┐       │
│  │           Agent Router (MCP Style)               │       │
│  │  - Query Analysis                                │       │
│  │  - Agent Selection                               │       │
│  │  - Context Management                            │       │
│  └──────────────────────────────────────────────────┘       │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              Specialized Agents Layer                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│  │  Code   │ │Document │ │  Task   │ │Research │          │
│  │  Agent  │ │  Agent  │ │  Agent  │ │  Agent  │          │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘          │
│       │           │           │           │                 │
│       └───────────┴───────────┴───────────┘                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                   RAG System                                 │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Document Processing                             │       │
│  │  - Load → Chunk → Embed → Store                 │       │
│  └──────────────────────────────────────────────────┘       │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Retrieval System                                │       │
│  │  - Semantic Search → Rerank → Context            │       │
│  └──────────────────────────────────────────────────┘       │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│               Data & Storage Layer                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │PostgreSQL│ │  Redis   │ │ChromaDB  │ │   S3/    │      │
│  │  (SQL)   │ │ (Cache)  │ │ (Vector) │ │FileSystem│      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend Layer (Next.js)

**Technology**: Next.js 14 with App Router, React, TypeScript, Tailwind CSS

**Components**:
- **Pages**: Landing, Auth (Login/Register), Dashboard
- **Features**: 
  - Chat interface with real-time messaging
  - Document upload and management
  - Task management UI
  - Universal search interface
- **State Management**: Zustand for global state
- **API Communication**: Axios with interceptors for auth

**Key Features**:
- Server-side rendering for performance
- Responsive design for all devices
- Real-time updates via WebSocket
- Progressive Web App capabilities

### 2. API Gateway (FastAPI)

**Technology**: FastAPI, Python 3.10+, Uvicorn

**Responsibilities**:
- Handle HTTP requests and WebSocket connections
- Authentication and authorization (JWT)
- Rate limiting and request validation
- API documentation (OpenAPI/Swagger)

**Endpoints**:
```
POST   /api/v1/users/register     - User registration
POST   /api/v1/users/login        - User login
GET    /api/v1/users/me           - Get current user

POST   /api/v1/chat/              - Send chat message
GET    /api/v1/chat/history/{id}  - Get chat history
GET    /api/v1/chat/list          - List all chats

POST   /api/v1/documents/upload   - Upload document
GET    /api/v1/documents/list     - List documents
DELETE /api/v1/documents/{id}     - Delete document

GET    /api/v1/tasks/list         - List tasks
POST   /api/v1/tasks/             - Create task
PUT    /api/v1/tasks/{id}         - Update task

GET    /api/v1/agents/list        - List available agents
```

### 3. LangChain Orchestration

**Technology**: LangChain, LangGraph

**Agent Router**:
```python
class AgentRouter:
    def route_query(query, context) -> agent_name
    def process_query(query, user_id, context) -> response
```

**Routing Logic**:
1. Analyze query for keywords and intent
2. Calculate confidence scores for each agent
3. Select agent with highest confidence (> 0.3)
4. Execute agent with full context
5. Return structured response

### 4. Multi-Agent System

#### Code Agent
- **Purpose**: Code analysis, debugging, generation
- **RAG Source**: Code repository (with syntax analysis)
- **Capabilities**:
  - Explain code functionality
  - Find bugs and suggest fixes
  - Generate new code
  - Analyze architecture
  - Create documentation

#### Document Agent
- **Purpose**: Document understanding and Q&A
- **RAG Source**: User's uploaded documents
- **Capabilities**:
  - Answer questions with citations
  - Summarize documents
  - Extract information
  - Compare documents
  - Find specific content

#### Task Agent
- **Purpose**: Task management and planning
- **RAG Source**: User's task history
- **Capabilities**:
  - Break down complex tasks
  - Estimate time requirements
  - Prioritize tasks
  - Suggest deadlines
  - Create action plans

#### Research Agent
- **Purpose**: General knowledge and research
- **RAG Source**: LLM knowledge (no RAG)
- **Capabilities**:
  - Answer general questions
  - Explain concepts
  - Provide educational content
  - Research topics
  - Synthesize information

### 5. RAG System

**Document Processing Pipeline**:
```
Upload → Validate → Load → Chunk → Embed → Store
```

**Components**:

1. **Document Loaders**:
   - PyPDFLoader (PDF files)
   - Docx2txtLoader (Word documents)
   - TextLoader (Plain text)
   - UnstructuredMarkdownLoader (Markdown)

2. **Text Splitter**:
   - RecursiveCharacterTextSplitter
   - Chunk size: 1000 characters
   - Overlap: 200 characters
   - Preserves semantic meaning

3. **Embeddings**:
   - Model: `text-embedding-3-small`
   - Dimensions: 1536
   - Provider: OpenAI

4. **Vector Store**:
   - Default: ChromaDB (local)
   - Alternative: Pinecone (cloud)
   - Collections per user
   - Metadata filtering

**Retrieval Process**:
```
Query → Embed → Similarity Search → Rerank → Context
```

### 6. Code RAG System

**Specialized for Code**:

```python
class CodeRAGSystem:
    def analyze_code_file(file_path) -> metadata
    def process_codebase(repo_path, user_id, project_id)
    def search_code(query, user_id, project_id)
```

**Features**:
- Language detection (Pygments)
- Python AST analysis (functions, classes)
- Multi-file repository support
- Smart code chunking
- Language-specific metadata

### 7. Data Layer

#### PostgreSQL
**Tables**:
- `users` - User accounts
- `documents` - Document metadata
- `chats` - Chat sessions
- `messages` - Chat messages
- `tasks` - User tasks

**Schema Design**:
- UUID primary keys
- Indexed foreign keys
- JSON metadata columns
- Timestamp tracking

#### Redis
**Usage**:
- Session caching
- Rate limiting
- Real-time data
- Temporary storage

#### ChromaDB (Vector Database)
**Collections**:
- `{user_id}_documents` - Document embeddings
- `{user_id}_code` - Code embeddings

**Metadata Schema**:
```json
{
  "document_id": "uuid",
  "user_id": "uuid",
  "filename": "string",
  "chunk_index": 0,
  "source": "file_path"
}
```

## Data Flow Examples

### Example 1: Chat Message

```
1. User types message → Frontend
2. POST /api/v1/chat/ → API Gateway
3. Save user message → PostgreSQL
4. Agent Router analyzes query
5. Route to appropriate agent (e.g., Document Agent)
6. Agent searches vector DB → ChromaDB
7. Retrieve relevant chunks
8. Format prompt with context
9. Call LLM (OpenAI) → Generate response
10. Save assistant message → PostgreSQL
11. Return response → Frontend
12. Display in chat UI
```

### Example 2: Document Upload

```
1. User selects file → Frontend
2. POST /api/v1/documents/upload → API Gateway
3. Validate file (type, size)
4. Save file → File System
5. Create document record → PostgreSQL (status: processing)
6. Background process:
   a. Load document
   b. Split into chunks
   c. Generate embeddings (OpenAI)
   d. Store in vector DB (ChromaDB)
7. Update document status → PostgreSQL (status: completed)
8. Notify frontend (WebSocket)
```

### Example 3: Code Analysis

```
1. User asks "Explain authentication flow"
2. Agent Router → Code Agent
3. Code Agent searches code embeddings
4. Retrieve relevant code snippets
5. Analyze AST metadata
6. Format code with line numbers
7. Generate explanation (LLM)
8. Return with source citations
```

## Security Architecture

### Authentication Flow

```
1. User login → API Gateway
2. Verify credentials → PostgreSQL
3. Generate JWT token
4. Return token → Frontend
5. Store token → LocalStorage
6. Include in all requests (Authorization header)
```

### Authorization

- JWT token validation on every request
- User ID extracted from token
- Resource ownership verification
- Role-based access control (future)

### Data Security

- Passwords hashed with bcrypt
- JWT tokens with expiration
- HTTPS in production
- SQL injection prevention (SQLAlchemy ORM)
- XSS prevention (React)
- CORS configuration

## Scalability Considerations

### Horizontal Scaling

- **Frontend**: Static site, can be deployed to CDN
- **Backend**: Stateless API, can run multiple instances
- **Database**: PostgreSQL replication
- **Vector DB**: Sharding by user_id

### Performance Optimization

- **Caching**: Redis for frequently accessed data
- **Background Jobs**: Celery for document processing
- **Connection Pooling**: SQLAlchemy + pgbouncer
- **CDN**: Static assets and media files

### Monitoring

- **Logging**: Structured JSON logs
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry
- **Error Tracking**: Sentry

## Technology Choices & Rationale

### Why FastAPI?
- Async support for better performance
- Automatic API documentation
- Type hints and validation (Pydantic)
- WebSocket support

### Why Next.js?
- Server-side rendering
- File-based routing
- API routes (if needed)
- Excellent developer experience

### Why LangChain?
- Unified interface for LLMs
- Built-in RAG patterns
- Agent frameworks
- Tool calling support

### Why ChromaDB?
- Easy local deployment
- Good performance
- Python native
- Open source

### Why PostgreSQL?
- ACID compliance
- JSON support
- Rich ecosystem
- Proven reliability

## Future Architecture Enhancements

1. **Microservices**: Split agents into separate services
2. **Message Queue**: RabbitMQ/Kafka for async processing
3. **Kubernetes**: Container orchestration
4. **Multi-tenancy**: Organization-level workspaces
5. **Plugin System**: Custom agent marketplace
6. **Graph Database**: For relationship queries
7. **Streaming**: Real-time response streaming
8. **Edge Computing**: Local model inference

---

**This architecture is designed to be:**
- ✅ Scalable
- ✅ Maintainable
- ✅ Secure
- ✅ Performant
- ✅ Extensible
