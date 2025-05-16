"""Client for external API services."""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from config import WISE_API_HEADERS, CUSTOMER_IDS

def get_tomorrow_date_range(days_ahead: int = 0) -> Tuple[datetime, datetime, datetime]:
    """
    Get tomorrow's date range for API requests.
    
    Args:
        days_ahead: Number of days ahead to calculate
        
    Returns:
        Tuple of (start_datetime, end_datetime, target_date)
    """
    target_date = datetime.now() + timedelta(days=days_ahead)
    start_datetime = target_date.replace(hour=0, minute=0, second=0)
    end_datetime = target_date.replace(hour=23, minute=59, second=59)
    return start_datetime, end_datetime, target_date

def get_outbound_orders(customer_ids: List[str] = None) -> List[Dict[str, Any]]:
    """
    Get outbound orders from status report for multiple customers.
    
    Args:
        customer_ids: List of customer IDs to fetch orders for. If None, uses all configured customer IDs.
        
    Returns:
        List of dictionaries containing outbound order information
    """
    if customer_ids is None:
        customer_ids = CUSTOMER_IDS
        
    tomorrow_start, tomorrow_end, _ = get_tomorrow_date_range()
    url = "https://wise.logisticsteam.com/v2/valleyview/report-center/outbound/order-status-report/search-by-paging"
    
    all_orders = []
    
    for customer_id in customer_ids:
        payload = {
            "statuses": ["Imported", "Open", "Planning", "Planned", "Committed"],
            "customerId": customer_id,
            "orderTypes": ["DropShip Order"],
            "appointmentTimeFrom": tomorrow_start.strftime('%Y-%m-%dT%H:%M:%S'),
            "appointmentTimeTo": tomorrow_end.strftime('%Y-%m-%dT%H:%M:%S'),
            "paging": {"pageNo": 1, "limit": 100}
        }
        
        try:
            response = requests.post(url, headers=WISE_API_HEADERS, json=payload)
            response.raise_for_status()
            
            data = response.json()
            orders = data.get('results', {}).get('data', [])
            
            # Process and standardize order data
            for order in orders:
                try:
                    pallet_qty = float(order.get('Pallet QTY', 0)) or 0
                    order_qty = float(order.get('Order QTY', 0)) or 0
                    picking_type = order.get('Picking Type', '')
                except (ValueError, TypeError):
                    pallet_qty = order_qty = 0
                    picking_type = ''
                    
                all_orders.append({
                    'order_no': order.get('Order No.'),
                    'status': order.get('Order Status', 'Unknown'),
                    'customer': order.get('Customer ID', 'Unknown'),
                    'customer_id': customer_id,  # Add customer_id to track which customer the order belongs to
                    'ship_to': order.get('Ship to', 'Unknown'),
                    'state': order.get('State', 'Unknown'),
                    'reference_no': order.get('Reference Number', ''),
                    'target_completion_date': order.get('Target Completion Date', ''),
                    'pallet_qty': pallet_qty,
                    'order_qty': order_qty,
                    'Picking Type': picking_type
                })
        
        except Exception as e:
            print(f"Error in outbound status report API for customer {customer_id}: {str(e)}")
            continue
    
    return all_orders