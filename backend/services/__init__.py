"""
Пакет сервисов для приложения AI Emotion Tracker.
Содержит модули для работы с базой данных, аутентификацией и OpenAI API.
"""

from .database import (
    create_user, get_user_by_id, get_user_by_username, update_user,
    create_journal_entry, get_journal_entry, get_user_journal_entries,
    update_journal_entry, delete_journal_entry,
    create_chat_session, get_chat_session, get_user_chat_sessions,
    add_message_to_chat, delete_chat_session, get_user_emotion_stats
)

from .auth import (
    verify_password, get_password_hash,
    create_access_token, decode_access_token, get_user_id_from_token
)

from .openai_service import (
    analyze_emotions, get_chat_response
)

__all__ = [
    'create_user', 'get_user_by_id', 'get_user_by_username', 'update_user',
    'create_journal_entry', 'get_journal_entry', 'get_user_journal_entries',
    'update_journal_entry', 'delete_journal_entry',
    'create_chat_session', 'get_chat_session', 'get_user_chat_sessions',
    'add_message_to_chat', 'delete_chat_session', 'get_user_emotion_stats',
    'verify_password', 'get_password_hash',
    'create_access_token', 'decode_access_token', 'get_user_id_from_token',
    'analyze_emotions', 'get_chat_response'
]
