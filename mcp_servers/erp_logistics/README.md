# ERP Logistics MCP Server

Enterprise Resource Planning integration server for Crisis Response Center logistics operations.

**Transport:** HTTP/REST API (FastAPI + uvicorn)

## Overview

This MCP server provides 8 tools for managing logistics operations via HTTP endpoints:

1. **get_inventory_levels** - Check stock levels across warehouses
2. **get_warehouse_info** - Get warehouse details and capacity
3. **get_shipment_status** - Track specific shipments
4. **get_all_shipments** - View all active shipments
5. **get_supplier_info** - Access supplier database
6. **check_item_availability** - Verify item availability
7. **get_warehouse_locations** - List warehouse locations
8. **calculate_reorder_point** - Determine reorder needs

## Architecture

```
ADK Agent (tools/erp_tools.py)
    ↓ HTTP POST
FastAPI Server (http://127.0.0.1:8000)
    ↓ Process
Mock ERP Database
```

## Files

- `server.py` - FastAPI server with HTTP endpoints
- `config.json` - Server metadata
- `README.md` - This file

## Running the Server

**Automatic (Recommended):**
```powershell
.\run.ps1  # Starts MCP server automatically
```

**Manual:**
```powershell
.\start_mcp_server.ps1
# Or:
python mcp_servers/erp_logistics/server.py
```

**Verify:**
```powershell
# Health check
Invoke-WebRequest http://127.0.0.1:8000/health

# List tools
Invoke-WebRequest http://127.0.0.1:8000/tools
```

## HTTP Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `GET /tools` - List all 8 tools
- `POST /tools/call` - Execute a tool

**Example:**
```powershell
# Call a tool
$body = @{
    name = "get_inventory_levels"
    arguments = @{ item_name = "medical_supplies" }
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/tools/call -Body $body -ContentType "application/json"
```

## Mock Data

Currently uses mock data for:
- **Items**: medical_supplies, water, food_rations, blankets, tents
- **Warehouses**: warehouse_a (North), warehouse_b (South), warehouse_c (East)
- **Shipments**: SHP-001 (in transit), SHP-002 (delivered), SHP-003 (pending)
- **Suppliers**: SUP-001, SUP-002, SUP-003

## Testing

```powershell
# System-wide test (includes MCP server health check)
python tests/test_system_ready.py
```

## Integration

The logistics agent uses HTTP to call ERP tools:
```python
from tools.erp_tools import get_inventory_levels

# Simple synchronous call
result = get_inventory_levels("medical_supplies")
print(result)
```

Under the hood:
```python
# HTTP POST to http://127.0.0.1:8000/tools/call
httpx.post(url, json={
    "name": "get_inventory_levels",
    "arguments": {"item_name": "medical_supplies"}
})
```

## Future: Real ERP Integration

To connect to a real ERP system:

1. Replace mock data dictionaries with API calls
2. Add authentication/authorization
3. Implement error handling for network failures
4. Add caching for performance
5. Set up real-time updates via webhooks

## Documentation

See [HTTP_TRANSPORT_MIGRATION.md](../../docs/HTTP_TRANSPORT_MIGRATION.md) for:
- Architecture comparison (stdio vs HTTP)
- Performance benchmarks
- Migration details
