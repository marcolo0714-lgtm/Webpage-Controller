from playwright.sync_api import sync_playwright
import sys
import time
from datetime import datetime

input_time = "23:59:59"  # Example input time in HH:MM:SS format

def time_difference(target_datetime):
    """
    Calculates the difference between target_datetime and the current time,
    and returns a formatted string: 'x hours y minutes z seconds'
    """
    now = datetime.now()
    
    # Get the total difference in seconds
    time_delta = target_datetime - now
    total_seconds = int(time_delta.total_seconds())
    if total_seconds <= 0:
        total_seconds += 86400
    
    # Math to extract hours, minutes, and remaining seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    return f"{hours} hours {minutes} minutes {seconds} seconds"

if __name__ == "__main__":
    now = datetime.now()
    target_time = datetime.strptime(input_time, "%H:%M:%S").time()
    target_datetime = datetime.combine(now.date(), target_time)

    print(time_difference(target_datetime))


