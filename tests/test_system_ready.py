"""
Test script to verify ADK application with ERP integration.
This simulates querying the logistics agent.
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 70)
print("TESTING CRISIS RESPONSE CENTER WITH ERP INTEGRATION")
print("=" * 70)
print()

# Test MCP Server connection
print("Step 1: Checking MCP Server health...")
try:
    from tools.erp_tools import _erp_client
    if _erp_client.check_health():
        print(f"[OK] MCP Server is healthy at {_erp_client.server_url}")
    else:
        print(f"[ERROR] MCP Server not responding at {_erp_client.server_url}")
        print("[ERROR] Please start the MCP server first:")
        print("  python mcp_servers\\erp_logistics\\server.py")
        exit(1)
except Exception as e:
    print(f"[ERROR] Cannot connect to MCP Server: {e}")
    exit(1)

print()

# Test loading the agent
print("Step 2: Loading logistics agent...")
try:
    from agents import logistics_agent
    print(f"[OK] Logistics agent loaded with {len(logistics_agent.tools)} tools")
except Exception as e:
    print(f"[ERROR] Failed to load logistics agent: {e}")
    exit(1)

print()

# Test ERP tool directly
print("Step 3: Testing ERP tool directly...")
try:
    from tools.erp_tools import get_inventory_levels
    result = get_inventory_levels("medical_supplies")
    print("Medical Supplies Inventory:")
    print(result)
    print("[OK] ERP tool works!")
except Exception as e:
    print(f"[ERROR] ERP tool failed: {e}")
    exit(1)

print()
print("=" * 70)
print("[OK] ALL SYSTEMS READY!")
print("=" * 70)
print()
print("The Crisis Response Center is ready to run.")
print()
print("To start the interactive application, run:")
print("  python -m google.adk.cli run .")
print()
print("Then query the agent with questions like:")
print("  - What medical supplies do we have?")
print("  - Track shipment SHP-001")
print("  - Do we have 500 blankets available?")
print()
