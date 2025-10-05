"""
Data models for the meeting bot.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class Update:
    """Represents a single update in a meeting."""
    user: str
    progress: str
    blockers: str
    goals: str
    timestamp: str
    
    def __post_init__(self):
        """Validate update data after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate update fields."""
        max_length = 500
        
        if not self.progress.strip():
            raise ValueError("Progress field is required")
        if not self.blockers.strip():
            raise ValueError("Blockers field is required")
        if not self.goals.strip():
            raise ValueError("Goals field is required")
        
        if len(self.progress) > max_length:
            raise ValueError(f"Progress field must be {max_length} characters or less")
        if len(self.blockers) > max_length:
            raise ValueError(f"Blockers field must be {max_length} characters or less")
        if len(self.goals) > max_length:
            raise ValueError(f"Goals field must be {max_length} characters or less")


@dataclass
class Meeting:
    """Represents a meeting with its updates."""
    id: str
    created_by: str
    created_at: str
    updates: List[Update]
    is_closed: bool = False
    closed_at: Optional[str] = None
    
    def add_update(self, user: str, progress: str, blockers: str, goals: str) -> Update:
        """Add a new update to the meeting."""
        if self.is_closed:
            raise ValueError("Cannot add updates to a closed meeting")
        
        update = Update(
            user=user,
            progress=progress,
            blockers=blockers,
            goals=goals,
            timestamp=datetime.now().isoformat()
        )
        
        self.updates.append(update)
        return update
    
    def close(self):
        """Close the meeting."""
        if self.is_closed:
            raise ValueError("Meeting is already closed")
        
        self.is_closed = True
        self.closed_at = datetime.now().isoformat()
    
    def to_dict(self):
        """Convert meeting to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'updates': [asdict(update) for update in self.updates],
            'is_closed': self.is_closed,
            'closed_at': self.closed_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Meeting':
        """Create meeting from dictionary."""
        updates = [Update(**update_data) for update_data in data.get('updates', [])]
        
        return cls(
            id=data['id'],
            created_by=data['created_by'],
            created_at=data['created_at'],
            updates=updates,
            is_closed=data.get('is_closed', False),
            closed_at=data.get('closed_at')
        )
    
    @classmethod
    def create_new(cls, created_by: str) -> 'Meeting':
        """Create a new meeting."""
        now = datetime.now()
        # Prefix ID with yy-m-d (e.g., 25-9-10) and append short random suffix for uniqueness
        date_prefix = f"{now.year % 100}-{now.month}-{now.day}"
        unique_suffix = uuid.uuid4().hex[:8]
        meeting_id = f"{date_prefix}-{unique_suffix}"
        return cls(
            id=meeting_id,
            created_by=created_by,
            created_at=now.isoformat(),
            updates=[]
        )

