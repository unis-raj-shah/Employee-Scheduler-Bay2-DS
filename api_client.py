"""Client for external API services."""

import requests
from typing import Dict, List, Any
from config import WISE_API_HEADERS, CUSTOMER_IDS

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
        
    url = "https://wise.logisticsteam.com/v2/valleyview/report-center/outbound/order-status-report/search-by-paging"
    
    all_orders = []
    
    for customer_id in customer_ids:
        payload = {
            "statuses": ["Imported", "Open", "Planning", "Planned", "Committed"],
            "customerId": customer_id,
            "orderTypes": ["DropShip Order"],
            "paging": {"pageNo": 1, "limit": 1000}
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
                    'customer_id': customer_id,
                    'ship_to': order.get('Ship to', 'Unknown'),
                    'state': order.get('State', 'Unknown'),
                    'reference_no': order.get('Reference Number', ''),
                    'target_completion_date': order.get('Target Completion Date', ''),
                    'pallet_qty': pallet_qty,
                    'order_qty': order_qty,
                    'Picking Type': picking_type
                })
            
            print(f"Retrieved {len(orders)} outbound orders for customer {customer_id}")
        
        except Exception as e:
            print(f"Error in outbound status report API for customer {customer_id}: {str(e)}")
            continue
    
    print(f"Total outbound orders retrieved: {len(all_orders)}")
    return all_orders

def get_picked_orders(customer_ids: List[str] = None) -> List[Dict[str, Any]]:
    """
    Get picked orders from status report.
    
    Returns:
        List of dictionaries containing picked order information
    """
    if customer_ids is None:
        customer_ids = CUSTOMER_IDS
    
    url = "https://wise.logisticsteam.com/v2/valleyview/report-center/outbound/order-status-report/search-by-paging"
    
    all_picked_orders = []
    
    for customer_id in customer_ids:
        payload = {
            "statuses": ["Picked"],
            "customerId": customer_id,
            "orderTypes": ["DropShip Order"],
            "paging": {"pageNo": 1, "limit": 1000}
        }
    
        try:
            response = requests.post(url, headers=WISE_API_HEADERS, json=payload)
            response.raise_for_status()
            
            data = response.json()
            orders = data.get('results', {}).get('data', [])
            
            # Process and standardize picked order data
            for order in orders:
                try:
                    raw_pallet_qty = order.get('Pallet QTY', 0)
                    raw_order_qty = order.get('Order QTY', 0)
                    
                    pallet_qty = float(raw_pallet_qty) if raw_pallet_qty and str(raw_pallet_qty).strip() else 0
                    order_qty = float(raw_order_qty) if raw_order_qty and str(raw_order_qty).strip() else 0
                    
                    all_picked_orders.append({
                        'order_no': order.get('Order No.'),
                        'status': order.get('Order Status', 'Unknown'),
                        'customer': order.get('Customer ID', 'Unknown'),
                        'ship_to': order.get('Ship to', 'Unknown'),
                        'state': order.get('State', 'Unknown'),
                        'reference_no': order.get('Reference Number', ''),
                        'target_completion_date': order.get('Target Completion Date', ''),
                        'pallet_qty': pallet_qty,
                        'order_qty': order_qty
                    })
                except (ValueError, TypeError):
                    continue
            
            print(f"Retrieved {len(orders)} picked orders for customer {customer_id}")
        
        except Exception as e:
            print(f"Error in outbound status report API for customer {customer_id}: {str(e)}")
            continue
    
    print(f"Total picked orders retrieved: {len(all_picked_orders)}")
    return all_picked_orders

def get_packed_staged_orders(customer_ids: List[str] = None) -> List[Dict[str, Any]]:
    """
    Get packed and staged orders from status report.
    
    Returns:
        List of dictionaries containing packed and staged order information
    """
    if customer_ids is None:
        customer_ids = CUSTOMER_IDS
    
    url = "https://wise.logisticsteam.com/v2/valleyview/report-center/outbound/order-status-report/search-by-paging"
    
    all_packed_staged_orders = []
    
    for customer_id in customer_ids:
        payload = {
            "statuses": ["Packed", "Staged"],
            "customerId": customer_id,
            "orderTypes": ["DropShip Order"],
            "paging": {"pageNo": 1, "limit": 1000}
        }
    
        try:
            response = requests.post(url, headers=WISE_API_HEADERS, json=payload)
            response.raise_for_status()
            
            data = response.json()
            orders = data.get('results', {}).get('data', [])
            
            # Process and standardize packed/staged order data
            for order in orders:
                try:
                    raw_pallet_qty = order.get('Pallet QTY', 0)
                    raw_order_qty = order.get('Order QTY', 0)
                    
                    pallet_qty = float(raw_pallet_qty) if raw_pallet_qty and str(raw_pallet_qty).strip() else 0
                    order_qty = float(raw_order_qty) if raw_order_qty and str(raw_order_qty).strip() else 0
                    
                    all_packed_staged_orders.append({
                        'order_no': order.get('Order No.'),
                        'status': order.get('Order Status', 'Unknown'),
                        'customer': order.get('Customer ID', 'Unknown'),
                        'ship_to': order.get('Ship to', 'Unknown'),
                        'state': order.get('State', 'Unknown'),
                        'reference_no': order.get('Reference Number', ''),
                        'target_completion_date': order.get('Target Completion Date', ''),
                        'pallet_qty': pallet_qty,
                        'order_qty': order_qty
                    })
                except (ValueError, TypeError):
                    continue
            
            print(f"Retrieved {len(orders)} packed/staged orders for customer {customer_id}")
        
        except Exception as e:
            print(f"Error in outbound status report API for customer {customer_id}: {str(e)}")
            continue
    
    print(f"Total packed/staged orders retrieved: {len(all_packed_staged_orders)}")
    return all_packed_staged_orders