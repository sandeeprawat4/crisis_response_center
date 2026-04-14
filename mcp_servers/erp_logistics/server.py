"""
ERP MCP Server - Middleware for Logistics Agent
Exposes ERP system tools with mock data for crisis response logistics.
HTTP Transport for production deployment.
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
import json
import os
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mock ERP Database
MOCK_INVENTORY = {
    "medical_supplies": {
        "warehouse_a": {"quantity": 450, "location": "North District", "last_updated": "2026-04-10"},
        "warehouse_b": {"quantity": 120, "location": "South District", "last_updated": "2026-04-10"},
        "warehouse_c": {"quantity": 280, "location": "East District", "last_updated": "2026-04-09"}
    },
    "water": {
        "warehouse_a": {"quantity": 2500, "location": "North District", "last_updated": "2026-04-10"},
        "warehouse_b": {"quantity": 1800, "location": "South District", "last_updated": "2026-04-10"},
        "warehouse_c": {"quantity": 950, "location": "East District", "last_updated": "2026-04-09"}
    },
    "food_rations": {
        "warehouse_a": {"quantity": 1200, "location": "North District", "last_updated": "2026-04-10"},
        "warehouse_b": {"quantity": 450, "location": "South District", "last_updated": "2026-04-10"},
        "warehouse_c": {"quantity": 680, "location": "East District", "last_updated": "2026-04-10"}
    },
    "blankets": {
        "warehouse_a": {"quantity": 890, "location": "North District", "last_updated": "2026-04-10"},
        "warehouse_b": {"quantity": 340, "location": "South District", "last_updated": "2026-04-09"},
        "warehouse_c": {"quantity": 520, "location": "East District", "last_updated": "2026-04-10"}
    },
    "tents": {
        "warehouse_a": {"quantity": 75, "location": "North District", "last_updated": "2026-04-10"},
        "warehouse_b": {"quantity": 32, "location": "South District", "last_updated": "2026-04-10"},
        "warehouse_c": {"quantity": 48, "location": "East District", "last_updated": "2026-04-09"}
    }
}

MOCK_SHIPMENTS = {
    "SHP-001": {
        "status": "in_transit",
        "item": "medical_supplies",
        "quantity": 150,
        "origin": "warehouse_a",
        "destination": "Emergency Site Alpha",
        "eta": "2026-04-10 18:00",
        "driver": "John Smith",
        "vehicle": "TRK-445"
    },
    "SHP-002": {
        "status": "delivered",
        "item": "water",
        "quantity": 500,
        "origin": "warehouse_b",
        "destination": "Shelter Beta",
        "eta": "2026-04-10 12:00",
        "driver": "Maria Garcia",
        "vehicle": "TRK-223"
    },
    "SHP-003": {
        "status": "pending",
        "item": "food_rations",
        "quantity": 300,
        "origin": "warehouse_a",
        "destination": "Distribution Center C",
        "eta": "2026-04-11 09:00",
        "driver": "Not assigned",
        "vehicle": "Not assigned"
    }
}

MOCK_SUPPLIERS = {
    "SUP-001": {
        "name": "Emergency Medical Supply Co.",
        "items": ["medical_supplies", "first_aid_kits"],
        "lead_time_days": 2,
        "reliability_score": 0.95,
        "contact": "supplies@emergency-med.com"
    },
    "SUP-002": {
        "name": "Regional Water Distribution",
        "items": ["water", "water_purification_tablets"],
        "lead_time_days": 1,
        "reliability_score": 0.98,
        "contact": "orders@regional-water.com"
    },
    "SUP-003": {
        "name": "Food Relief International",
        "items": ["food_rations", "nutrition_packs"],
        "lead_time_days": 3,
        "reliability_score": 0.92,
        "contact": "relief@food-intl.org"
    }
}

MOCK_WAREHOUSES = {
    "warehouse_a": {
        "location": "North District",
        "address": "123 Industrial Blvd, North District",
        "capacity": 10000,
        "current_utilization": 0.65,
        "manager": "Alice Johnson",
        "operating_hours": "24/7"
    },
    "warehouse_b": {
        "location": "South District",
        "address": "456 Logistics Lane, South District",
        "capacity": 7500,
        "current_utilization": 0.48,
        "manager": "Bob Chen",
        "operating_hours": "06:00-22:00"
    },
    "warehouse_c": {
        "location": "East District",
        "address": "789 Supply Street, East District",
        "capacity": 8000,
        "current_utilization": 0.52,
        "manager": "Carmen Rodriguez",
        "operating_hours": "24/7"
    }
}

# Create MCP Server instance
server = Server("erp-logistics-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available ERP tools."""
    return [
        Tool(
            name="get_inventory_levels",
            description="Get current inventory levels for a specific item across all warehouses from the ERP system",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_name": {
                        "type": "string",
                        "description": "Name of the item (e.g., medical_supplies, water, food_rations, blankets, tents)"
                    }
                },
                "required": ["item_name"]
            }
        ),
        Tool(
            name="get_warehouse_info",
            description="Get detailed information about a specific warehouse including capacity, location, and utilization",
            inputSchema={
                "type": "object",
                "properties": {
                    "warehouse_id": {
                        "type": "string",
                        "description": "Warehouse identifier (e.g., warehouse_a, warehouse_b, warehouse_c)"
                    }
                },
                "required": ["warehouse_id"]
            }
        ),
        Tool(
            name="get_shipment_status",
            description="Track the status of a shipment by ID from the ERP logistics system",
            inputSchema={
                "type": "object",
                "properties": {
                    "shipment_id": {
                        "type": "string",
                        "description": "Shipment tracking ID (e.g., SHP-001, SHP-002)"
                    }
                },
                "required": ["shipment_id"]
            }
        ),
        Tool(
            name="get_all_shipments",
            description="Get status of all active and recent shipments from the ERP system",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_supplier_info",
            description="Get information about suppliers including lead times, items they supply, and reliability scores",
            inputSchema={
                "type": "object",
                "properties": {
                    "supplier_id": {
                        "type": "string",
                        "description": "Supplier identifier (e.g., SUP-001, SUP-002) or leave empty to get all suppliers"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="check_item_availability",
            description="Check if a specific item is available in sufficient quantity across all warehouses",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_name": {
                        "type": "string",
                        "description": "Name of the item to check"
                    },
                    "required_quantity": {
                        "type": "integer",
                        "description": "Minimum required quantity"
                    }
                },
                "required": ["item_name", "required_quantity"]
            }
        ),
        Tool(
            name="get_warehouse_locations",
            description="Get all warehouse locations and their basic information",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="calculate_reorder_point",
            description="Calculate if an item needs reordering based on current stock levels and consumption rate",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_name": {
                        "type": "string",
                        "description": "Name of the item to check for reordering"
                    },
                    "daily_consumption": {
                        "type": "integer",
                        "description": "Average daily consumption rate"
                    }
                },
                "required": ["item_name", "daily_consumption"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls to the ERP system."""
    
    if name == "get_inventory_levels":
        item_name = arguments["item_name"]
        if item_name in MOCK_INVENTORY:
            inventory_data = MOCK_INVENTORY[item_name]
            total_quantity = sum(wh["quantity"] for wh in inventory_data.values())
            
            result = {
                "item": item_name,
                "total_quantity": total_quantity,
                "warehouses": inventory_data,
                "timestamp": datetime.now().isoformat()
            }
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Item '{item_name}' not found in ERP system"})
            )]
    
    elif name == "get_warehouse_info":
        warehouse_id = arguments["warehouse_id"]
        if warehouse_id in MOCK_WAREHOUSES:
            warehouse_data = MOCK_WAREHOUSES[warehouse_id]
            # Add current inventory summary
            inventory_summary = {}
            for item, warehouses in MOCK_INVENTORY.items():
                if warehouse_id in warehouses:
                    inventory_summary[item] = warehouses[warehouse_id]["quantity"]
            
            result = {
                **warehouse_data,
                "warehouse_id": warehouse_id,
                "current_inventory": inventory_summary
            }
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Warehouse '{warehouse_id}' not found"})
            )]
    
    elif name == "get_shipment_status":
        shipment_id = arguments["shipment_id"]
        if shipment_id in MOCK_SHIPMENTS:
            shipment_data = MOCK_SHIPMENTS[shipment_id]
            return [TextContent(
                type="text",
                text=json.dumps({
                    "shipment_id": shipment_id,
                    **shipment_data
                }, indent=2)
            )]
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Shipment '{shipment_id}' not found"})
            )]
    
    elif name == "get_all_shipments":
        all_shipments = {sid: sdata for sid, sdata in MOCK_SHIPMENTS.items()}
        return [TextContent(
            type="text",
            text=json.dumps(all_shipments, indent=2)
        )]
    
    elif name == "get_supplier_info":
        supplier_id = arguments.get("supplier_id")
        if supplier_id:
            if supplier_id in MOCK_SUPPLIERS:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "supplier_id": supplier_id,
                        **MOCK_SUPPLIERS[supplier_id]
                    }, indent=2)
                )]
            else:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": f"Supplier '{supplier_id}' not found"})
                )]
        else:
            return [TextContent(
                type="text",
                text=json.dumps(MOCK_SUPPLIERS, indent=2)
            )]
    
    elif name == "check_item_availability":
        item_name = arguments["item_name"]
        required_quantity = arguments["required_quantity"]
        
        if item_name in MOCK_INVENTORY:
            inventory_data = MOCK_INVENTORY[item_name]
            total_quantity = sum(wh["quantity"] for wh in inventory_data.values())
            
            available_warehouses = [
                {"warehouse": wh_id, "quantity": wh_data["quantity"], "location": wh_data["location"]}
                for wh_id, wh_data in inventory_data.items()
                if wh_data["quantity"] > 0
            ]
            
            result = {
                "item": item_name,
                "required_quantity": required_quantity,
                "total_available": total_quantity,
                "sufficient": total_quantity >= required_quantity,
                "shortage": max(0, required_quantity - total_quantity),
                "available_at": available_warehouses
            }
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Item '{item_name}' not found"})
            )]
    
    elif name == "get_warehouse_locations":
        locations = {
            wh_id: {
                "location": wh_data["location"],
                "address": wh_data["address"],
                "manager": wh_data["manager"],
                "operating_hours": wh_data["operating_hours"]
            }
            for wh_id, wh_data in MOCK_WAREHOUSES.items()
        }
        return [TextContent(
            type="text",
            text=json.dumps(locations, indent=2)
        )]
    
    elif name == "calculate_reorder_point":
        item_name = arguments["item_name"]
        daily_consumption = arguments["daily_consumption"]
        
        if item_name in MOCK_INVENTORY:
            inventory_data = MOCK_INVENTORY[item_name]
            total_quantity = sum(wh["quantity"] for wh in inventory_data.values())
            
            # Simple reorder logic: if stock covers less than 7 days, reorder
            days_of_stock = total_quantity / daily_consumption if daily_consumption > 0 else float('inf')
            reorder_threshold = daily_consumption * 7  # 7 days safety stock
            needs_reorder = total_quantity < reorder_threshold
            
            # Find suppliers for this item
            available_suppliers = [
                {"supplier_id": sup_id, "name": sup_data["name"], "lead_time_days": sup_data["lead_time_days"]}
                for sup_id, sup_data in MOCK_SUPPLIERS.items()
                if item_name in sup_data["items"]
            ]
            
            result = {
                "item": item_name,
                "current_stock": total_quantity,
                "daily_consumption": daily_consumption,
                "days_of_stock_remaining": round(days_of_stock, 1),
                "reorder_threshold": reorder_threshold,
                "needs_reorder": needs_reorder,
                "recommended_order_quantity": max(0, reorder_threshold * 2 - total_quantity) if needs_reorder else 0,
                "available_suppliers": available_suppliers
            }
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Item '{item_name}' not found"})
            )]
    
    else:
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"})
        )]


# ============================================================================
# FastAPI HTTP Transport
# ============================================================================

app = FastAPI(title="ERP MCP Server", version="1.0.0")


class ToolCallRequest(BaseModel):
    """Request model for tool calls."""
    name: str
    arguments: Dict[str, Any]


class ToolListResponse(BaseModel):
    """Response model for tool listing."""
    tools: list


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "erp-logistics-server", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/tools")
async def get_tools():
    """List all available tools."""
    tools = await list_tools()
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            }
            for tool in tools
        ]
    }


@app.post("/tools/call")
async def call_tool_endpoint(request: ToolCallRequest):
    """Execute a tool by name with arguments."""
    try:
        result = await call_tool(request.name, request.arguments)
        
        # Extract text from TextContent
        if result and len(result) > 0:
            response_text = result[0].text
            try:
                # Try to parse as JSON for cleaner response
                response_data = json.loads(response_text)
                return JSONResponse(content=response_data)
            except json.JSONDecodeError:
                return {"result": response_text}
        
        return {"error": "No result returned from tool"}
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "tool": request.name}
        )


def start_server(host: str = None, port: int = None):
    """Start the HTTP server."""
    # Read from environment variables with fallback to defaults
    host = host or os.getenv("ERP_SERVER_HOST", "127.0.0.1")
    port = port or int(os.getenv("ERP_SERVER_PORT", "8000"))
    
    print(f"[OK] Starting ERP MCP Server on http://{host}:{port}")
    print(f"[OK] Health check: http://{host}:{port}/health")
    print(f"[OK] Tools list: http://{host}:{port}/tools")
    print(f"[OK] Call tool: POST http://{host}:{port}/tools/call")
    print(f"[INFO] Configuration: HOST={host}, PORT={port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    start_server()
