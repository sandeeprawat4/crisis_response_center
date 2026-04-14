"""
ERP Tools Wrapper for Google ADK Integration

This module provides Python function wrappers around the ERP MCP server tools,
making them compatible with Google ADK agents.

Uses HTTP transport for clean, production-ready integration.
"""

import json
import logging
import os
from typing import Dict, Any
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# MCP Server Configuration (from environment)
ERP_SERVER_HOST = os.getenv("ERP_SERVER_HOST", "127.0.0.1")
ERP_SERVER_PORT = os.getenv("ERP_SERVER_PORT", "8000")
ERP_SERVER_URL = os.getenv("ERP_SERVER_URL", f"http://{ERP_SERVER_HOST}:{ERP_SERVER_PORT}")


class ERPClient:
    """Client to interact with ERP MCP Server via HTTP."""
    
    def __init__(self, server_url: str = ERP_SERVER_URL):
        self.server_url = server_url
        self.tools_endpoint = f"{server_url}/tools/call"
        self.health_endpoint = f"{server_url}/health"
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an ERP tool via HTTP.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Dictionary of arguments for the tool
            
        Returns:
            Dictionary containing the tool result or error
        """
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    self.tools_endpoint,
                    json={"name": tool_name, "arguments": arguments}
                )
                response.raise_for_status()
                return response.json()
        
        except httpx.ConnectError:
            logger.error(f"Cannot connect to ERP MCP Server at {self.server_url}")
            return {
                "error": f"ERP MCP Server not available at {self.server_url}. Please run: python mcp_servers\\erp_logistics\\server.py"
            }
        except httpx.TimeoutException:
            logger.error(f"Timeout calling ERP tool {tool_name}")
            return {"error": f"Timeout calling {tool_name}"}
        except Exception as e:
            logger.error(f"Error calling ERP tool {tool_name}: {e}")
            return {"error": f"Failed to call {tool_name}: {str(e)}"}
    
    def check_health(self) -> bool:
        """Check if the ERP server is healthy."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(self.health_endpoint)
                return response.status_code == 200
        except:
            return False


# Global ERP client instance
_erp_client = ERPClient()


# ============================================================================
# ERP Tool Functions for Google ADK Agents
# ============================================================================

def get_inventory_levels(item_name: str) -> str:
    """
    Get current inventory levels for a specific item across all warehouses.
    
    Args:
        item_name: Name of the item (e.g., medical_supplies, water, food_rations, blankets, tents)
    
    Returns:
        JSON string with inventory data including total quantity and warehouse breakdown
    """
    data = _erp_client.call_tool("get_inventory_levels", {"item_name": item_name})
    
    # Format for better readability
    if "error" not in data:
        total = data.get("total_quantity", 0)
        warehouses = data.get("warehouses", {})
        
        summary = f"Inventory for {item_name}:\n"
        summary += f"Total: {total} units\n\n"
        for wh_id, wh_data in warehouses.items():
            summary += f"{wh_id} ({wh_data['location']}): {wh_data['quantity']} units\n"
        
        return summary
    
    return json.dumps(data)


def get_warehouse_info(warehouse_id: str) -> str:
    """
    Get detailed information about a specific warehouse.
    
    Args:
        warehouse_id: Warehouse identifier (warehouse_a, warehouse_b, warehouse_c)
    
    Returns:
        JSON string with warehouse details including capacity, location, and current inventory
    """
    data = _erp_client.call_tool("get_warehouse_info", {"warehouse_id": warehouse_id})
    
    if "error" not in data:
        summary = f"Warehouse {warehouse_id}:\n"
        summary += f"Location: {data.get('location', 'N/A')}\n"
        summary += f"Address: {data.get('address', 'N/A')}\n"
        summary += f"Manager: {data.get('manager', 'N/A')}\n"
        summary += f"Capacity: {data.get('capacity', 0)} units\n"
        summary += f"Utilization: {data.get('current_utilization', 0)*100:.1f}%\n"
        summary += f"Hours: {data.get('operating_hours', 'N/A')}\n\n"
        
        inventory = data.get('current_inventory', {})
        if inventory:
            summary += "Current Inventory:\n"
            for item, qty in inventory.items():
                summary += f"  - {item}: {qty} units\n"
        
        return summary
    
    return json.dumps(data)


def get_shipment_status(shipment_id: str) -> str:
    """
    Track the status of a specific shipment.
    
    Args:
        shipment_id: Shipment tracking ID (e.g., SHP-001)
    
    Returns:
        JSON string with shipment details including status, location, and ETA
    """
    data = _erp_client.call_tool("get_shipment_status", {"shipment_id": shipment_id})
    
    if "error" not in data:
        summary = f"Shipment {shipment_id}:\n"
        summary += f"Status: {data.get('status', 'N/A').upper()}\n"
        summary += f"Item: {data.get('item', 'N/A')}\n"
        summary += f"Quantity: {data.get('quantity', 0)} units\n"
        summary += f"From: {data.get('origin', 'N/A')}\n"
        summary += f"To: {data.get('destination', 'N/A')}\n"
        summary += f"ETA: {data.get('eta', 'N/A')}\n"
        summary += f"Driver: {data.get('driver', 'N/A')}\n"
        summary += f"Vehicle: {data.get('vehicle', 'N/A')}\n"
        
        return summary
    
    return json.dumps(data)


def get_all_shipments() -> str:
    """
    Get status of all active and recent shipments.
    
    Returns:
        JSON string with all shipments data
    """
    data = _erp_client.call_tool("get_all_shipments", {})
    
    summary = "All Shipments:\n\n"
    for ship_id, ship_data in data.items():
        summary += f"{ship_id} - {ship_data.get('status', 'N/A').upper()}\n"
        summary += f"  Item: {ship_data.get('item', 'N/A')} ({ship_data.get('quantity', 0)} units)\n"
        summary += f"  Route: {ship_data.get('origin', 'N/A')} → {ship_data.get('destination', 'N/A')}\n"
        summary += f"  ETA: {ship_data.get('eta', 'N/A')}\n\n"
    
    return summary


def check_item_availability(item_name: str, required_quantity: int) -> str:
    """
    Check if a specific item is available in sufficient quantity.
    
    Args:
        item_name: Name of the item
        required_quantity: Minimum required quantity
    
    Returns:
        JSON string with availability status and warehouse locations
    """
    data = _erp_client.call_tool("check_item_availability", {
        "item_name": item_name,
        "required_quantity": required_quantity
    })
    
    if "error" not in data:
        sufficient = data.get('sufficient', False)
        total = data.get('total_available', 0)
        shortage = data.get('shortage', 0)
        
        summary = f"Availability Check for {item_name}:\n"
        summary += f"Required: {required_quantity} units\n"
        summary += f"Available: {total} units\n"
        
        if sufficient:
            summary += "[OK] SUFFICIENT - We have enough stock\n\n"
        else:
            summary += f"[WARNING] INSUFFICIENT - Short by {shortage} units\n\n"
        
        summary += "Available at:\n"
        for location in data.get('available_at', []):
            summary += f"  - {location['warehouse']} ({location['location']}): {location['quantity']} units\n"
        
        return summary
    
    return json.dumps(data)


def get_warehouse_locations() -> str:
    """
    Get all warehouse locations and basic information.
    
    Returns:
        JSON string with warehouse locations
    """
    data = _erp_client.call_tool("get_warehouse_locations", {})
    
    summary = "Warehouse Locations:\n\n"
    for wh_id, wh_data in data.items():
        summary += f"{wh_id}:\n"
        summary += f"  Location: {wh_data.get('location', 'N/A')}\n"
        summary += f"  Address: {wh_data.get('address', 'N/A')}\n"
        summary += f"  Manager: {wh_data.get('manager', 'N/A')}\n"
        summary += f"  Hours: {wh_data.get('operating_hours', 'N/A')}\n\n"
    
    return summary


def calculate_reorder_point(item_name: str, daily_consumption: int) -> str:
    """
    Calculate if an item needs reordering based on consumption rate.
    
    Args:
        item_name: Name of the item
        daily_consumption: Average daily consumption rate
    
    Returns:
        JSON string with reorder analysis and recommendations
    """
    data = _erp_client.call_tool("calculate_reorder_point", {
        "item_name": item_name,
        "daily_consumption": daily_consumption
    })
    
    if "error" not in data:
        needs_reorder = data.get('needs_reorder', False)
        days_left = data.get('days_of_stock_remaining', 0)
        current = data.get('current_stock', 0)
        threshold = data.get('reorder_threshold', 0)
        
        summary = f"Reorder Analysis for {item_name}:\n"
        summary += f"Current Stock: {current} units\n"
        summary += f"Daily Usage: {daily_consumption} units\n"
        summary += f"Days Remaining: {days_left} days\n"
        summary += f"Reorder Threshold: {threshold} units (7 days safety stock)\n\n"
        
        if needs_reorder:
            recommended = data.get('recommended_order_quantity', 0)
            summary += f"[WARNING] REORDER NEEDED\n"
            summary += f"Recommended Order: {recommended} units\n\n"
            
            suppliers = data.get('available_suppliers', [])
            if suppliers:
                summary += "Available Suppliers:\n"
                for sup in suppliers:
                    summary += f"  - {sup['name']} (Lead time: {sup['lead_time_days']} days)\n"
        else:
            summary += "[OK] Stock levels adequate - no reorder needed\n"
        
        return summary
    
    return json.dumps(data)


def get_supplier_info(supplier_id: str = None) -> str:
    """
    Get information about suppliers.
    
    Args:
        supplier_id: Optional supplier ID, or None for all suppliers
    
    Returns:
        JSON string with supplier information
    """
    args = {"supplier_id": supplier_id} if supplier_id else {}
    data = _erp_client.call_tool("get_supplier_info", args)
    
    if "error" not in data:
        if supplier_id:
            # Single supplier
            summary = f"Supplier {supplier_id}:\n"
            summary += f"Name: {data.get('name', 'N/A')}\n"
            summary += f"Items: {', '.join(data.get('items', []))}\n"
            summary += f"Lead Time: {data.get('lead_time_days', 0)} days\n"
            summary += f"Reliability: {data.get('reliability_score', 0)*100:.0f}%\n"
            summary += f"Contact: {data.get('contact', 'N/A')}\n"
        else:
            # All suppliers
            summary = "All Suppliers:\n\n"
            for sup_id, sup_data in data.items():
                summary += f"{sup_id} - {sup_data.get('name', 'N/A')}\n"
                summary += f"  Items: {', '.join(sup_data.get('items', []))}\n"
                summary += f"  Lead Time: {sup_data.get('lead_time_days', 0)} days\n"
                summary += f"  Reliability: {sup_data.get('reliability_score', 0)*100:.0f}%\n\n"
        
        return summary
    
    return json.dumps(data)
