"""
LEEF (Log Event Extended Format) formatter implementation.

Formats log events according to the IBM LEEF specification used by
McAfee Web Gateway and other security products.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import re

from .base import LogFormatter, LogEvent


class LEEFFormatter(LogFormatter):
    """
    Formats log events in LEEF format.
    
    LEEF format structure:
    LEEF:Version|Vendor|Product|Version|EventID|key1=value1|key2=value2|...
    """
    
    def __init__(self, output_dir: Path):
        """Initialize LEEF formatter."""
        super().__init__(output_dir)
        self.vendor = "McAfee"
        self.product = "Web Gateway"
        self.product_version = "10.15.0.623"
        self.leef_version = "2.0"
        self.current_file = None
        self.current_date = None
    
    def _escape_value(self, value: str) -> str:
        """
        Escape special characters in LEEF values.
        
        LEEF requires escaping of pipe (|) and backslash (\) characters.
        """
        if not isinstance(value, str):
            value = str(value)
        value = value.replace('\\', '\\\\')
        value = value.replace('|', '\\|')
        value = value.replace('\n', '\\n')
        value = value.replace('\r', '\\r')
        return value
    
    def _get_event_id(self, event: LogEvent) -> str:
        """
        Determine the event ID based on the event type.
        
        For McAfee Web Gateway, using 302 for web traffic events.
        """
        return "302"  # Web traffic event
    
    def format_event(self, event: LogEvent) -> str:
        """
        Format a log event in LEEF format.
        
        Args:
            event: The event to format
            
        Returns:
            LEEF formatted string
        """
        # Build LEEF header
        header = f"LEEF:{self.leef_version}|{self.vendor}|{self.product}|{self.product_version}|{self._get_event_id(event)}|"
        
        # Format timestamp
        dev_time = event.timestamp.strftime('%b %d %Y %H:%M:%S.%f')[:-3]
        
        # Build key-value pairs for essential fields in tab-separated format
        fields = []
        
        # Core fields in the expected order
        fields.append(f"devTime={dev_time}")
        fields.append(f"src={event.source_ip}")
        fields.append(f"dst={event.destination_ip}")
        fields.append(f"usrName={self._escape_value(event.username)}")
        fields.append(f"request={self._escape_value(event.url)}")
        fields.append(f"action={event.action}")
        fields.append(f"cat={self._escape_value(event.category)}")
        
        # Optional fields that may be included
        if event.service_name and event.service_name != 'Internet':
            fields.append(f"app={self._escape_value(event.service_name)}")
        
        # Combine header and fields with tab separator
        leef_line = header + '\t'.join(fields)
        
        return leef_line
    
    def write_event(self, event: LogEvent) -> None:
        """
        Write a formatted event to the appropriate log file.
        
        Log files are organized by date: leef_YYYYMMDD.log
        """
        # Determine file name based on event date
        event_date = event.timestamp.date()
        
        # Check if we need to open a new file
        if self.current_date != event_date or self._file_handle is None:
            # Close previous file if open
            if self._file_handle:
                self._file_handle.close()
            
            # Open new file
            filename = f"leef_{event_date.strftime('%Y%m%d')}.log"
            filepath = self.output_dir / filename
            self._file_handle = open(filepath, 'a', encoding='utf-8')
            self.current_date = event_date
            self.current_file = filepath
        
        # Format and write the event
        leef_line = self.format_event(event)
        self._file_handle.write(leef_line + '\n')
        self._file_handle.flush()  # Ensure data is written
    
    def write_batch(self, events: list[LogEvent]) -> None:
        """
        Write a batch of events efficiently.
        
        Args:
            events: List of events to write
        """
        # Group events by date
        events_by_date = {}
        for event in events:
            event_date = event.timestamp.date()
            if event_date not in events_by_date:
                events_by_date[event_date] = []
            events_by_date[event_date].append(event)
        
        # Write each group
        for date, date_events in sorted(events_by_date.items()):
            filename = f"leef_{date.strftime('%Y%m%d')}.log"
            filepath = self.output_dir / filename
            
            with open(filepath, 'a', encoding='utf-8') as f:
                for event in date_events:
                    leef_line = self.format_event(event)
                    f.write(leef_line + '\n')