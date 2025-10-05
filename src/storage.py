"""
Storage system for meetings using JSON files.
"""
import json
from pathlib import Path
from typing import Optional, List
from .models import Meeting


class MeetingStorage:
    """Handles storage and retrieval of meetings using JSON files."""
    
    def __init__(self, storage_dir: str = "json"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def _get_meeting_path(self, meeting_id: str) -> Path:
        """Get the file path for a meeting."""
        meeting_dir = self.storage_dir / meeting_id
        meeting_dir.mkdir(exist_ok=True)
        return meeting_dir / "meeting.json"
    
    def save_meeting(self, meeting: Meeting) -> None:
        """Save a meeting to storage."""
        meeting_path = self._get_meeting_path(meeting.id)
        
        with open(meeting_path, 'w', encoding='utf-8') as f:
            json.dump(meeting.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_meeting(self, meeting_id: str) -> Optional[Meeting]:
        """Load a meeting from storage."""
        meeting_path = self._get_meeting_path(meeting_id)
        
        if not meeting_path.exists():
            return None
        
        try:
            with open(meeting_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Meeting.from_dict(data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading meeting {meeting_id}: {e}")
            return None
    
    def meeting_exists(self, meeting_id: str) -> bool:
        """Check if a meeting exists."""
        meeting_path = self._get_meeting_path(meeting_id)
        return meeting_path.exists()
    
    def list_meetings(self) -> List[str]:
        """List all meeting IDs."""
        if not self.storage_dir.exists():
            return []
        
        meeting_ids = []
        for meeting_dir in self.storage_dir.iterdir():
            if meeting_dir.is_dir() and (meeting_dir / "meeting.json").exists():
                meeting_ids.append(meeting_dir.name)
        
        return meeting_ids
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a meeting and its directory."""
        meeting_path = self._get_meeting_path(meeting_id)
        
        if not meeting_path.exists():
            return False
        
        try:
            # Delete the meeting file
            meeting_path.unlink()
            
            # Delete the meeting directory if it's empty
            meeting_dir = meeting_path.parent
            if meeting_dir.exists() and not any(meeting_dir.iterdir()):
                meeting_dir.rmdir()
            
            return True
        except OSError as e:
            print(f"Error deleting meeting {meeting_id}: {e}")
            return False

