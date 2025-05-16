"""Main application for warehouse scheduler."""

import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import schedule_service
from notification_service import send_short_staffed_notification
from database import retrieve_employees

# Initialize FastAPI app
app = FastAPI(
    title="Warehouse Scheduler API",
    description="API for calculating warehouse staffing requirements",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Warehouse Scheduler API",
        "version": "1.0.0",
        "endpoints": {
            "/api/schedule": "Get warehouse scheduling data",
            "/docs": "API documentation (Swagger UI)",
            "/redoc": "API documentation (ReDoc)"
        }
    }

@app.get("/api/schedule")
async def get_schedule() -> Dict[str, Any]:
    """
    Get warehouse scheduling data.
    
    Returns:
        Dict containing scheduling data including required staff and forecast.
    
    Raises:
        HTTPException: If there's an error generating the schedule.
    """
    try:
        scheduling_data = schedule_service.run_scheduler()
        if not scheduling_data:
            raise HTTPException(
                status_code=404,
                detail="No scheduling data available"
            )
        return {
            'success': True,
            'data': scheduling_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating schedule: {str(e)}"
        )

def format_role_name(role: str) -> str:
    """
    Format role name by removing prefixes and capitalizing.
    
    Args:
        role: The role name to format
        
    Returns:
        Formatted role name
    """
    # Remove 'outbound_' prefix if present
    if role.startswith('outbound_'):
        role = role[9:]
    # Capitalize first letter of each word
    return ' '.join(word.capitalize() for word in role.split('_'))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--api":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        print(f"Starting API server on port {port}")
        print(f"API documentation available at:")
        print(f"  - http://localhost:{port}/docs")
        print(f"  - http://localhost:{port}/redoc")
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
    else:
        print("\n=== Warehouse Shift Scheduler ===")
        result = schedule_service.run_scheduler()
        if result:
            print("\nForecast:")
            print(f"- Cases to Pick: {result['forecast_data']['cases_to_pick']:.1f}")
            
            print("\nRequired Staff:")
            for role, count in result['required_roles'].items():
                if isinstance(count, dict):
                    for sub_role, sub_count in count.items():
                        print(f"- {format_role_name(sub_role)}: {sub_count}")
                else:
                    print(f"- {format_role_name(role)}: {count}")

            # Calculate shortages based on available employees in the database
            required_roles = result['required_roles']
            matched_employees = retrieve_employees(required_roles)

            shortages = {}
            for role, required_count in required_roles.items():
                if isinstance(required_count, dict):
                    # Handle nested role structure
                    for sub_role, sub_count in required_count.items():
                        available_count = len(matched_employees.get(f"{role}_{sub_role}", []))
                        if available_count < sub_count:
                            shortages[f"{role}_{sub_role}"] = sub_count - available_count
                else:
                    # Handle flat role structure
                    available_count = len(matched_employees.get(role, []))
                    if available_count < required_count:
                        shortages[role] = required_count - available_count

            if shortages:
                print("\nShortages (based on available employees):")
                for role, shortage in shortages.items():
                    print(f"- {format_role_name(role)}: {shortage}")
                send_short_staffed_notification(shortages)
        else:
            print("\nNo scheduling data available")