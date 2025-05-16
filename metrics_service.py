"""Service for calculating warehouse metrics and required roles."""

from typing import Dict, Any, List
import pandas as pd
from datetime import datetime, timedelta
from config import DEFAULT_METRICS

def get_metrics_summary() -> Dict[str, Any]:
    """
    Get summary of warehouse metrics.
    
    Returns:
        Dictionary containing metrics summaries
    """
    try:
        # Use default metrics from config
        return DEFAULT_METRICS
        
    except Exception as e:
        print(f"Error calculating metrics summary: {str(e)}")
        return {}

def calculate_required_roles(metrics_summaries: Dict[str, Any], forecast_data: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
    """
    Calculate required staff based on metrics and forecast.
    
    Args:
        metrics_summaries: Dictionary of metrics summaries
        forecast_data: Dictionary of forecast data
        
    Returns:
        Dictionary of required roles by operation
    """
    required_roles = {}
    
    try:
        # Constants
        effective_work_mins_per_person = 360 # 7 hours * 60 minutes
        
        # Get forecast data
        cases_to_pick = forecast_data.get("cases_to_pick", 0)
        
        # Calculate outbound roles
        if "outbound" in metrics_summaries and (cases_to_pick > 0):
            outbound = metrics_summaries["outbound"]
            
            # Calculate picking time
            total_pick_time = cases_to_pick * outbound.get("avg_pick_time", 1.0)
            required_roles["picker_outbound"] = max(1, round(total_pick_time / effective_work_mins_per_person))
            
            # Calculate packing time
            total_pack_time = cases_to_pick * outbound.get("avg_pack_time", 2.0)
            required_roles["packer_outbound"] = max(1, round(total_pack_time / effective_work_mins_per_person))
            
            # Calculate processing time
            total_process_time = cases_to_pick * outbound.get("avg_process_time", 1.5)
            required_roles["processor_outbound"] = max(1, round(total_process_time / effective_work_mins_per_person))
        
        # Format the roles by operation
        formatted_roles = {
            "outbound": {
                "picker": required_roles.get("picker_outbound", 0),
                "packer": required_roles.get("packer_outbound", 0),
                "processor": required_roles.get("processor_outbound", 0),
                "forklift_driver": 2  # Always need at least 2 forklift drivers
            }
        }
        
        return formatted_roles
        
    except Exception as e:
        print(f"Error calculating required roles: {str(e)}")
        return {}