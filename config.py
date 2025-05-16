"""Configuration settings for the warehouse scheduler application."""

import os
from typing import List, Dict, Any

# API Settings
WISE_API_HEADERS = {
    "authorization": os.getenv("WISE_API_KEY", "6d95c4d1-a408-4cc4-b1e1-04f3485ec78a"),
    "wise-company-id": os.getenv("WISE_COMPANY_ID", "ORG-1"),
    "wise-facility-id": os.getenv("WISE_FACILITY_ID", "F1"),
    "content-type": "application/json;charset=UTF-8",
    "user": os.getenv("WISE_USER", "rshah")
}

# Email Configuration
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.office365.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "sender_email": os.getenv("SENDER_EMAIL", "raj.shah@unisco.com"),
    "sender_password": os.getenv("SENDER_PASSWORD", "T%058811678539oy"),
    "default_recipients": os.getenv("DEFAULT_RECIPIENTS", "raj.shah@unisco.com").split(',') #,mark.tuttle@unisco.com,john.diaz@unisco.com,carlos.morales@unisco.com,steven.balbas@unisco.com,ricardo.tapia.@unisco.com").split(',')
}

# Database Settings
DB_PATH = os.getenv("DB_PATH", "./chroma_db")

# Customer Settings
CUSTOMER_IDS = os.getenv("CUSTOMER_IDS", "ORG-655338,ORG-606771,ORG-644329,ORG-214099,ORG-665253,ORG-616507,ORG-698137,ORG-641207,ORG-34818,ORG-654546,ORG-554407,ORG-625900,ORG-625904,ORG-625905,ORG-629731,ORG-625907,ORG-306334,ORG-660613,ORG-660956,ORG-40861,ORG-43365,ORG-617365,ORG-654693,ORG-318716,ORG-723580,ORG-697433,ORG-702440,ORG-697437,ORG-658062,ORG-708068,ORG-697434,ORG-664534,ORG-697432,ORG-697438,ORG-676237").split(',')  # Comma-separated list of customer IDs
DEFAULT_CUSTOMER_ID = CUSTOMER_IDS[0]  # Keep for backward compatibility

# Role mappings for consistent matching
ROLE_MAPPINGS = {
    'picker': ['picker', 'order picker', 'warehouse picker'],
    'packer': ['packer', 'order packer', 'warehouse packer'],
    'stager': ['stager', 'order stager', 'warehouse stager']
}

# Efficiency factor for workforce calculations (as a decimal)
WORKFORCE_EFFICIENCY = 0.8

# Work hours per shift
HOURS_PER_SHIFT = 7.5

# Default metrics summaries
DEFAULT_METRICS = {
    "outbound": {
        "avg_pick_time": 1.0,  # minutes per case
        "avg_pack_time": 0.6,  # minutes per case
        "avg_process_time": 0.6,
    }
}

# Default shift schedule
DEFAULT_SHIFT = {
    "start_time": "6:00 AM",
    "end_time": "2:30 PM",
    "lunch_duration": "30 Mins",
    "location": "Buena Park, CA"
}