from .rag_system import search_disaster_protocols, rebuild_rag_index


def model_flood_spread(water_level_rise: float, terrain_type: str) -> str:
    """
    Simulates flood spread based on rising water levels and geography.
    Args:
        water_level_rise: The projected increase in meters.
        terrain_type: Type of land (e.g., 'urban', 'wetland', 'mountain').
    """
    # In practice, the Intelligence Agent may use 'code_execution=True' 
    # to write its own logic for this based on live inputs.
    risk_factor = 1.5 if terrain_type == "urban" else 0.8
    impact_area = water_level_rise * risk_factor * 10 
    return f"Estimated impact area: {impact_area} square kilometers."
