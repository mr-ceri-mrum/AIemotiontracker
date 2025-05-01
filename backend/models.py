"""
Модели данных для API.
Определяют структуру данных для запросов и ответов API.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

# Модели для пользователей
class UserBase(BaseModel):
    """Базовая модель пользователя"""
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email пользователя")

class UserCreate(UserBase):
    """Модель для создания пользователя"""
    password: str = Field(..., min_length=8, description="Пароль пользователя")

class User(UserBase):
    """Модель пользователя"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID пользователя")
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания")
    premium: bool = Field(default=False, description="Статус премиум-подписки")
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Модель для входа пользователя"""
    username: str = Field(..., description="Имя пользователя")
    password: str = Field(..., description="Пароль пользователя")

class Token(BaseModel):
    """Модель токена доступа"""
    access_token: str = Field(..., description="Токен доступа")
    token_type: str = Field(..., description="Тип токена")

class TokenData(BaseModel):
    """Данные из токена"""
    username: Optional[str] = None

# Модели для дневника эмоций
class JournalEntryBase(BaseModel):
    """Базовая модель записи дневника"""
    content: str = Field(..., min_length=1, max_length=5000, description="Текст записи")

class JournalEntryCreate(JournalEntryBase):
    """Модель для создания записи дневника"""
    pass

class JournalEntry(JournalEntryBase):
    """Модель записи дневника"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID записи")
    user_id: str = Field(..., description="ID пользователя")
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления")
    emotions: Optional[Dict[str, float]] = Field(None, description="Оценки эмоций")
    dominant_emotion: Optional[str] = Field(None, description="Доминирующая эмоция")
    analysis: Optional[str] = Field(None, description="Анализ эмоционального состояния")
    recommendations: Optional[str] = Field(None, description="Рекомендации")
    
    class Config:
        from_attributes = True

class JournalEntryUpdate(BaseModel):
    """Модель для обновления записи дневника"""
    content: Optional[str] = Field(None, min_length=1, max_length=5000, description="Текст записи")

class EmotionAnalysisResult(BaseModel):
    """Результат анализа эмоций"""
    emotions: Dict[str, float] = Field(..., description="Оценки эмоций")
    dominant_emotion: str = Field(..., description="Доминирующая эмоция")
    analysis: str = Field(..., description="Анализ эмоционального состояния")
    recommendations: str = Field(..., description="Рекомендации")

# Модели для чата
class ChatMessageBase(BaseModel):
    """Базовая модель сообщения чата"""
    content: str = Field(..., min_length=1, max_length=5000, description="Текст сообщения")

class ChatMessageCreate(ChatMessageBase):
    """Модель для создания сообщения чата"""
    pass

class ChatMessage(ChatMessageBase):
    """Модель сообщения чата"""
    role: str = Field(..., description="Роль отправителя (user/assistant)")
    timestamp: datetime = Field(default_factory=datetime.now, description="Время отправки")
    
    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    """Базовая модель сессии чата"""
    user_id: str = Field(..., description="ID пользователя")

class ChatSessionCreate(ChatSessionBase):
    """Модель для создания сессии чата"""
    pass

class ChatSession(ChatSessionBase):
    """Модель сессии чата"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID сессии")
    messages: List[ChatMessage] = Field(default_factory=list, description="Сообщения в сессии")
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания")
    updated_at: datetime = Field(default_factory=datetime.now, description="Дата обновления")
    
    class Config:
        from_attributes = True

# Модели для статистики
class EmotionStats(BaseModel):
    """Статистика эмоций"""
    period_days: int = Field(..., description="Период (в днях)")
    total_entries: int = Field(..., description="Общее количество записей")
    emotion_trends: Dict[str, float] = Field(..., description="Тренды эмоций")
    dominant_emotions: List[Dict[str, Any]] = Field(..., description="Доминирующие эмоции")
    
    class Config:
        from_attributes = True
