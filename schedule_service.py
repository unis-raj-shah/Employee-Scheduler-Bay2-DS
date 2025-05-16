"""Service for warehouse scheduling operations."""

from typing import Dict, List, Any, Optional
from metrics_service import get_metrics_summary, calculate_required_roles
from database import retrieve_employees
from api_client import get_outbound_orders, get_picked_orders, get_packed_staged_orders
from notification_service import send_schedule_email

def get_orders_for_scheduling():
    """
    Get all orders needed for scheduling.
    
    Returns:
        Dictionary containing forecast data
    """
    try:
        # Get orders from API
        outbound_orders = get_outbound_orders()
        picked_orders = get_picked_orders()
        packed_staged_orders = get_packed_staged_orders()
        
        # Calculate forecast data
        total_shipping_pallets = sum(order.get('pallet_qty', 0) for order in outbound_orders)
        total_order_qty = sum(order.get('order_qty', 0) for order in outbound_orders)
        
        # Calculate cases to pick - count all orders
        cases_to_pick = total_order_qty
        
        print(f"Total orders: {len(outbound_orders)}")
        print(f"Total order quantity: {total_order_qty}")
        print(f"Total cases to pick: {cases_to_pick}")
        
        # Calculate picked orders
        total_picked_orders = len(picked_orders)
        
        # Calculate packed/staged orders
        total_packed_staged_orders = len(packed_staged_orders)
        
        forecast_data = {
            'daily_shipping_pallets': total_shipping_pallets,
            'daily_order_qty': total_order_qty,
            'cases_to_pick': cases_to_pick,
            'picked_orders': picked_orders,
            'total_picked_orders': total_picked_orders,
            'packed_staged_orders': packed_staged_orders,
            'total_packed_staged_orders': total_packed_staged_orders
        }
        
        return forecast_data
        
    except Exception as e:
        print(f"Error getting orders for scheduling: {str(e)}")
        return {}

def assign_employees_to_roles(required_roles: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Assign employees to the calculated required roles.
    
    Args:
        required_roles: Dictionary of roles and their required counts
        
    Returns:
        Dictionary mapping roles to lists of assigned employees
    """
    assigned_employees = {}
    
    try:
        # Flatten the nested role structure
        flattened_roles = {}
        for operation, roles in required_roles.items():
            for role, count in roles.items():
                role_key = f"{operation}_{role}"
                flattened_roles[role_key] = count
        
        # Get employees matching the required roles
        matched_employees = retrieve_employees(flattened_roles)
        
        # For each role, assign the required number of employees
        for role, count in flattened_roles.items():
            available_employees = matched_employees.get(role, [])
            if len(available_employees) < count:
                print(f"Warning: Not enough employees for role {role}. Need {count}, found {len(available_employees)}")
            
            # Assign up to the required number of employees
            assigned_employees[role] = available_employees[:count]
    
    except Exception as e:
        print(f"Error assigning employees to roles: {e}")
    
    return assigned_employees

def run_scheduler() -> Optional[Dict[str, Any]]:
    """
    Run warehouse shift scheduler.
    
    Returns:
        Dictionary containing scheduling data or None if no data
    """
    metrics_summaries = get_metrics_summary()
    forecast_data = get_orders_for_scheduling()
    
    if not forecast_data:
        return None
    
    required_roles = calculate_required_roles(metrics_summaries, forecast_data)
    
    # Get forecast data
    shipping_pallets = forecast_data.get("daily_shipping_pallets", 0)
    total_cases = forecast_data.get("daily_order_qty", 0)
    cases_to_pick = forecast_data.get("cases_to_pick", 0)
    
    # Calculate total picked orders
    picked_orders = forecast_data.get("picked_orders", [])
    total_picked_orders = len(picked_orders)
    
    # Calculate total packed/staged orders
    packed_staged_orders = forecast_data.get("packed_staged_orders", [])
    total_packed_staged_orders = len(packed_staged_orders)
    
    # Calculate estimated pallets for loading (30 orders/cases per pallet)
    ORDERS_PER_PALLET = 30
    estimated_pallets = max(1, round(total_packed_staged_orders / ORDERS_PER_PALLET))
    
    # Assign employees to roles
    assigned_employees = assign_employees_to_roles(required_roles)
    
    schedule_data = {
        'required_roles': required_roles,
        'assigned_employees': assigned_employees,
        'forecast_data': {
            'shipping_pallets': shipping_pallets,
            'order_qty': total_cases,
            'cases_to_pick': cases_to_pick,
            'total_picked_orders': total_picked_orders,
            'total_packed_staged_orders': total_packed_staged_orders,
            'estimated_pallets': estimated_pallets
        }
    }
    
    # Send schedule emails to assigned employees
    send_schedule_email(schedule_data, assigned_employees)
    
    # Send forecast email to the team
    from notification_service import send_forecast_email
    forecast_email_data = {
        'shipping_pallets': shipping_pallets,
        'cases_to_pick': cases_to_pick,
        'total_picked_orders': total_picked_orders,
        'total_packed_staged_orders': total_packed_staged_orders,
        'estimated_pallets': estimated_pallets
    }
    send_forecast_email(forecast_email_data, required_roles)
    
    return schedule_data