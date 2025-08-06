"""Service for warehouse metrics calculations."""

from typing import Dict, Any, List
from config import DEFAULT_METRICS, HOURS_PER_SHIFT, WORKFORCE_EFFICIENCY

def get_metrics_summary() -> Dict[str, Any]:
    """
    Get summary of warehouse metrics.
    
    Returns:
        Dictionary containing metrics summary
    """
    try:
        # Use default metrics directly
        metrics_summary = {
            'picking_rate': DEFAULT_METRICS['outbound']['avg_pick_time'],
            'processing_rate': DEFAULT_METRICS['outbound']['avg_process_time'],
            'packing_rate': DEFAULT_METRICS['outbound']['avg_pack_time'],
            'loading_rate': DEFAULT_METRICS['outbound']['avg_load_time']  # Using pack time as base for loading
        }
        
        return metrics_summary
        
    except Exception as e:
        print(f"Error getting metrics summary: {str(e)}")
        return {}

def calculate_required_roles(metrics_summary: Dict[str, Any], forecast_data: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
    """
    Calculate required roles based on metrics and forecast data.
    
    Args:
        metrics_summary: Dictionary containing metrics summary
        forecast_data: Dictionary containing forecast data
        
    Returns:
        Dictionary mapping operations to required roles and counts
    """
    try:
        # Get metrics
        picking_rate = metrics_summary.get('picking_rate', 0)
        processing_rate = metrics_summary.get('processing_rate', 0)
        packing_rate = metrics_summary.get('packing_rate', 0)
        loading_rate = metrics_summary.get('loading_rate', 0)
        
        # Get forecast data
        cases_to_pick = forecast_data.get('cases_to_pick', 0)
        total_picked_orders = forecast_data.get('total_picked_orders', 0)
        total_packed_staged_orders = forecast_data.get('total_packed_staged_orders', 0)
        
        # Calculate estimated pallets for loading (30 orders/cases per pallet)
        ORDERS_PER_PALLET = 30
        estimated_pallets = max(1, round(total_packed_staged_orders / ORDERS_PER_PALLET))
        
        # Calculate total minutes available per shift
        minutes_per_shift = HOURS_PER_SHIFT * 60 * WORKFORCE_EFFICIENCY
        
        print(f"Total packed/staged orders: {total_packed_staged_orders}")
        print(f"Estimated pallets for loading: {estimated_pallets}")
        
        # Calculate required staff for each operation
        required_roles = {
            'picking': {
                'picker': max(1, round((cases_to_pick * picking_rate) / minutes_per_shift)) if picking_rate > 0 else 1
            },
            'processing': {
                'processor': max(1, round(((total_picked_orders + cases_to_pick)) * (processing_rate + packing_rate) / minutes_per_shift)) if processing_rate > 0 else 1
            },
            'loading': {
                'forklift_driver': max(1, round((estimated_pallets * loading_rate) / minutes_per_shift)) if loading_rate > 0 else 1
            }
        }
        
        return required_roles
        
    except Exception as e:
        print(f"Error calculating required roles: {str(e)}")
        return {
            'picking': {'picker': 1},
            'processing': {'processor': 1},
            'loading': {'forklift_driver': 1}
        }