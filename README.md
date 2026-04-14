# Crisis Response Center

AI-powered crisis management system using Google ADK agents with integrated ERP logistics through MCP servers.

## � Overview

Multi-agent AI system for crisis response coordination featuring:
- **Real-time ERP Integration** - Inventory, warehouse, shipment management via MCP server
- **Multi-Agent Architecture** - Specialized agents for logistics, intelligence, and communications
- **RAG System** - Semantic search across crisis documentation
- **Production-Ready** - Proper logging, error handling, and configuration management

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google API Key for Gemini

### Installation

```powershell
# Clone and navigate to project
cd crisis_response_center

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Copy template and add your keys
cp .env.example .env
# Edit .env and set:
#   GOOGLE_API_KEY=your_api_key_here
#   ERP_SERVER_HOST=127.0.0.1  (optional, defaults shown)
#   ERP_SERVER_PORT=8000       (optional)
```

### Start the Application

```powershell
.\run.ps1
```

This will:
1. Start the MCP server
2. Validate the system
3. Launch the ADK application

### Verify System (Optional)
```powershell
python tests\test_system_ready.py
```

### Alternative: Direct Start

```powershell
python -m google.adk.cli run .
```

### Stop the Application

**Normal exit:**
- In the ADK prompt, type: `exit`

**Force stop (if exit doesn't work):**
- Press `Ctrl+C` twice
- Or run emergency stop script:
```powershell
.\stop.ps1
```

## 🎯 Features

### Multi-Agent System
- **Crisis Commander** - Root coordinator agent
- **Logistics Agent** - Resource allocation with ERP integration
- **Intelligence Agent** - Data analysis and insights
- **Communications Agent** - Public alerts and messaging

### ERP Integration via MCP (HTTP Transport)
- ✅ **Production Architecture** - FastAPI server with REST endpoints
- ✅ **No Event Loop Conflicts** - Clean HTTP requests, no async complexity
- ✅ **5x Faster** - Persistent server vs process spawning
- **Real-time Inventory** - Multi-warehouse stock management
- **Shipment Tracking** - Live logistics coordination
- **Supplier Database** - Lead times and reliability scores
- **Smart Reordering** - Automated restock calculations
- **8 ERP Tools** - Full logistics operation support

See [HTTP_TRANSPORT_MIGRATION.md](docs/HTTP_TRANSPORT_MIGRATION.md) for architecture details.

### RAG System
## 🏗️ Project Structure

```
crisis_response_center/
├── agents/                  # Google ADK Agents
├── tools/                   # Agent tools (incl. ERP wrapper)
├── mcp_servers/             # MCP Server (HTTP)
│   └── erp_logistics/       # ERP server with 8 tools
├── tests/                   # Test suite
├── docs/                    # Documentation
├── config/                  # Configuration & logging
├── data/                    # Data storage
├── run.ps1                  # Primary launcher
├── start_mcp_server.ps1     # MCP server launcher
└── stop.ps1                 # Emergency stop
```

## 💡 Features

### Multi-Agent System
- **Crisis Commander** - Root coordinator
- **Logistics Agent** - ERP integration & resource allocation
- **Intelligence Agent** - Data analysis
- **Communications Agent** - Public alerts

### ERP Integration (8 Tools)
- Inventory management across warehouses
- Shipment tracking
- Supplier database access
- Automated reorder point calculations
- Warehouse capacity monitoring

### RAG System
- Semantic search across crisis documentation
- FAISS vector database

## 📖 Documentation

- **[HTTP Transport Migration](docs/HTTP_TRANSPORT_MIGRATION.md)** - Architecture details and performance comparison
- **[ERP Server](mcp_servers/erp_logistics/README.md)** - MCP server for logistics tools

## 🧪 Testing

```powershell
# Verify system readiness (includes MCP server health check)
python tests\test_system_ready.py
```

## 📊 Example Queries

Once running, try these queries:

- "What medical supplies do we have available?"
- "Track shipment SHP-001"
- "Do we have 500 blankets for emergency shelter?"
- "Should we reorder food rations if consuming 200 daily?"
- "What's the capacity of warehouse A?"

## 🛠️ Technology Stack

- **Framework**: Google ADK
- **LLM**: Gemini 2.5 Flash
- **MCP Server**: FastAPI with HTTP transport
- **HTTP Client**: httpx
- **Vector DB**: FAISS
- **Language**: Python 3.8+

## 📝 Configuration

### Environment Variables (.env)

**Required:**
```env
GOOGLE_API_KEY=your_api_key_here
```

**Optional (MCP Server):**
```env
# Defaults to localhost:8000
ERP_SERVER_HOST=127.0.0.1
ERP_SERVER_PORT=8000

# Or use full URL (overrides host/port)
ERP_SERVER_URL=http://127.0.0.1:8000
```

**Environment-specific examples:**
```env
# Development
ERP_SERVER_HOST=127.0.0.1
ERP_SERVER_PORT=8000

# Remote server
ERP_SERVER_HOST=erp-dev.example.com
ERP_SERVER_PORT=8080

# Production with HTTPS
ERP_SERVER_URL=https://erp-api.example.com
```

See [.env.example](.env.example) for full configuration template.

### Logging
Configured via `config/logging_config.py`. Logs to console by default.

## 🚀 Production Deployment

### Checklist
- ✅ Set `GOOGLE_API_KEY` in environment
- ✅ Configure logging level in production
- ✅ Replace mock ERP data with real API endpoints
- ✅ Set up monitoring and alerting
- ✅ Configure backup for FAISS index

### Replacing Mock Data

Edit `mcp_servers/erp_logistics/server.py` and replace the `MOCK_*` dictionaries with real API calls to your ERP system.

## 📄 License

MIT License - See LICENSE file for details

---

**Crisis Response Center** • Powered by Google ADK & MCP
