import requests

def check_inventory(item_name: str, region: str) -> dict:
    """
    Queries the central ERP system for emergency supply levels.
    """
    # Example of a deterministic API call to a logistics system
    return {"item": item_name, "status": "In Stock", "count": 450, "location": region}

def reroute_shipment(shipment_id: str, new_destination: str) -> str:
    """
    Changes the delivery address of an active supply truck via the Transit API.
    """
    # This is a 'High-Stakes' tool that requires clear confirmation 
    # if using ADK guardrail callbacks.
    return f"Shipment {shipment_id} successfully rerouted to {new_destination}."

def get_shelter_capacity() -> str:
    """Retrieves live occupancy data for local emergency shelters."""
    return "Shelter Alpha: 80% full, Shelter Beta: 20% full."
