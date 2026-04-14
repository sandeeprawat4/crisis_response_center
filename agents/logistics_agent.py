"""
Logistics Agent - Crisis Response Center

Manages resource allocation and ERP integrations via MCP server tools.
Coordinates supply chains, inventory, warehouses, and shipments.
"""

import logging
from google.adk.agents import LlmAgent, ParallelAgent
from tools import check_inventory, reroute_shipment, get_shelter_capacity
from tools.erp_tools import (
    get_inventory_levels,
    get_warehouse_info,
    get_shipment_status,
    get_all_shipments,
    check_item_availability,
    get_warehouse_locations,
    calculate_reorder_point,
    get_supplier_info
)

# Configure logging
logger = logging.getLogger(__name__)

# ERP Tools are available as Python functions
# They communicate with the MCP server in the background
erp_tools = [
    get_inventory_levels,
    get_warehouse_info,
    get_shipment_status,
    get_all_shipments,
    check_item_availability,
    get_warehouse_locations,
    calculate_reorder_point,
    get_supplier_info
]

logger.info(f"Loaded {len(erp_tools)} ERP tools for logistics operations")

def check_warehouse_a(item: str): return f"Warehouse A: 50 units of {item} available."
def check_warehouse_b(item: str): return f"Warehouse B: 12 units of {item} available."

worker_a = LlmAgent(
    name="worker_a",
    instruction="Check Warehouse A for inventory.",
    tools=[check_warehouse_a]
)

worker_b = LlmAgent(
    name="worker_b",
    instruction="Check Warehouse B for inventory.",
    tools=[check_warehouse_b]
)

# Parallel check simulates high-speed resource allocation
logistics_worker = ParallelAgent(
    name="inventory_checker",
    sub_agents=[worker_a, worker_b]
)

# Logistics agent configuration with MCP server connection
logistics_agent = LlmAgent(
    name="logistics_agent",
    description="Manages resource allocation and ERP integrations via MCP server.",
    instruction="""
    You are the Logistics Coordinator with access to the Enterprise Resource Planning (ERP) system.
    
    Your responsibilities:
    - Monitor inventory levels across all warehouses using ERP tools
    - Track shipment status and coordinate deliveries
    - Check item availability and calculate reorder points
    - Provide warehouse information and supplier details
    - Ensure efficient resource allocation during crisis situations
    
    You have access to the following ERP system tools via MCP server:
    - get_inventory_levels: Check stock levels for specific items across warehouses
    - get_warehouse_info: Get detailed warehouse information
    - get_shipment_status: Track individual shipments
    - get_all_shipments: View all active shipments
    - get_supplier_info: Access supplier database
    - check_item_availability: Verify if items are available in required quantities
    - get_warehouse_locations: List all warehouse locations
    - calculate_reorder_point: Determine if items need reordering
    
    Use inventory_checker for quick parallel warehouse checks when needed.
    Always provide accurate, data-driven responses based on ERP system information.
    
    When queried about logistics, inventory, or supply chain matters:
    1. Use ERP tools to get current data
    2. Provide specific quantities and locations
    3. Highlight any supply shortages or concerns
    4. Recommend actions based on data
    """,
    sub_agents=[logistics_worker],
    tools=[*erp_tools, check_inventory, reroute_shipment, get_shelter_capacity]
)
