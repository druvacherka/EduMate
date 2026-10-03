"""Voice Tutoring Session Lifecycle Engine for EduMate.

Handles metadata logging, language preferences, and duration metrics for
voice tutoring interactions in English, Hindi, and Telugu without bloating database
storage with unnecessary raw audio binaries.
"""

import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from database import record_voice_session, list_voice_sessions
from backend.schemas import VoiceSessionCreateRequest, VoiceSessionResponse


class VoiceEngine:
    """Manages metadata lifecycle for voice interaction sessions."""

    def log_session(self, req: VoiceSessionCreateRequest, student_id: int = 1) -> VoiceSessionResponse:
        """Record voice session metrics."""
        session_id = f"voice-{uuid.uuid4().hex[:8]}"
        res = record_voice_session(
            session_id=session_id,
            language=req.language,
            topic=req.topic,
            goal_id=req.goal_id,
            duration_seconds=req.duration_seconds,
            transcript_summary=req.transcript_summary,
            student_id=student_id,
        )
        return VoiceSessionResponse(
            id=res["id"],
            language=res["language"],
            topic=res.get("topic"),
            duration_seconds=res.get("duration_seconds", 0),
            created_at=res.get("created_at", datetime.now().isoformat()),
        )

    def get_recent_sessions(self, student_id: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch past voice tutoring sessions."""
        return list_voice_sessions(student_id=student_id, limit=limit)


voice_engine = VoiceEngine()
