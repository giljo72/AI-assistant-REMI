# src/utils/document_formatting.py

from datetime import datetime, timezone, timedelta
import humanize
import logging

logger = logging.getLogger(__name__)

def format_timestamp(timestamp, include_time=False):
    """Format a timestamp for display
    
    Args:
        timestamp: Timestamp to format
        include_time: Whether to include the time
        
    Returns:
        Formatted timestamp string
    """
    if not timestamp:
        return "N/A"
    
    # Ensure timestamp is timezone-aware
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    
    # Get current time
    now = datetime.now(timezone.utc)
    
    # If timestamp is today
    if timestamp.date() == now.date():
        if include_time:
            return f"Today at {timestamp.strftime('%I:%M %p')}"
        return "Today"
    
    # If timestamp is yesterday
    yesterday = now - timedelta(days=1)
    if timestamp.date() == yesterday.date():
        if include_time:
            return f"Yesterday at {timestamp.strftime('%I:%M %p')}"
        return "Yesterday"
    
    # If timestamp is less than 7 days ago
    if now - timestamp < timedelta(days=7):
        if include_time:
            return f"{humanize.naturalday(timestamp)} at {timestamp.strftime('%I:%M %p')}"
        return humanize.naturalday(timestamp)
    
    # Otherwise, return the date
    if include_time:
        return timestamp.strftime("%b %d, %Y at %I:%M %p")
    return timestamp.strftime("%b %d, %Y")

def format_file_size(size_bytes):
    """Format file size for display
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted file size string
    """
    if not size_bytes:
        return "0 B"
    
    return humanize.naturalsize(size_bytes)