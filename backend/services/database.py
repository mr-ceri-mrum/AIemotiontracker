"""
Сервис для работы с базой данных MongoDB.
Включает функции для работы с пользователями, журналами эмоций и чатами.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Инициализация подключения к MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.emotion_tracker_db

# Коллекции
users_collection = db.users
journal_entries_collection = db.journal_entries
chat_sessions_collection = db.chat_sessions

# Функции для работы с пользователями
async def create_user(user_data: Dict[str, Any]) -> str:
    """
    Создает нового пользователя в базе данных.
    
    Args:
        user_data (Dict[str, Any]): Данные пользователя
        
    Returns:
        str: ID созданного пользователя
    """
    try:
        # Проверяем, существует ли пользователь с таким именем
        existing_user = await users_collection.find_one({"username": user_data["username"]})
        if existing_user:
            raise ValueError(f"Пользователь с именем {user_data['username']} уже существует")
        
        # Добавляем дату создания, если ее нет
        if "created_at" not in user_data:
            user_data["created_at"] = datetime.now()
        
        # Вставляем пользователя в базу
        result = await users_collection.insert_one(user_data)
        return str(result.inserted_id)
    
    except Exception as e:
        logger.error(f"Ошибка при создании пользователя: {str(e)}")
        raise

async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Получает пользователя по ID.
    
    Args:
        user_id (str): ID пользователя
        
    Returns:
        Optional[Dict[str, Any]]: Данные пользователя или None, если пользователь не найден
    """
    try:
        user = await users_collection.find_one({"id": user_id})
        return user
    
    except Exception as e:
        logger.error(f"Ошибка при получении пользователя по ID: {str(e)}")
        return None

async def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Получает пользователя по имени пользователя.
    
    Args:
        username (str): Имя пользователя
        
    Returns:
        Optional[Dict[str, Any]]: Данные пользователя или None, если пользователь не найден
    """
    try:
        user = await users_collection.find_one({"username": username})
        return user
    
    except Exception as e:
        logger.error(f"Ошибка при получении пользователя по имени: {str(e)}")
        return None

async def update_user(user_id: str, update_data: Dict[str, Any]) -> bool:
    """
    Обновляет данные пользователя.
    
    Args:
        user_id (str): ID пользователя
        update_data (Dict[str, Any]): Данные для обновления
        
    Returns:
        bool: True, если обновление успешно, иначе False
    """
    try:
        result = await users_collection.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    except Exception as e:
        logger.error(f"Ошибка при обновлении пользователя: {str(e)}")
        return False

# Функции для работы с записями дневника
async def create_journal_entry(entry_data: Dict[str, Any]) -> str:
    """
    Создает новую запись в дневнике эмоций.
    
    Args:
        entry_data (Dict[str, Any]): Данные записи
        
    Returns:
        str: ID созданной записи
    """
    try:
        # Добавляем дату создания, если ее нет
        if "created_at" not in entry_data:
            entry_data["created_at"] = datetime.now()
        
        # Вставляем запись в базу
        result = await journal_entries_collection.insert_one(entry_data)
        return str(result.inserted_id)
    
    except Exception as e:
        logger.error(f"Ошибка при создании записи дневника: {str(e)}")
        raise

async def get_journal_entry(entry_id: str) -> Optional[Dict[str, Any]]:
    """
    Получает запись дневника по ID.
    
    Args:
        entry_id (str): ID записи
        
    Returns:
        Optional[Dict[str, Any]]: Данные записи или None, если запись не найдена
    """
    try:
        entry = await journal_entries_collection.find_one({"id": entry_id})
        return entry
    
    except Exception as e:
        logger.error(f"Ошибка при получении записи дневника по ID: {str(e)}")
        return None

async def get_user_journal_entries(user_id: str, limit: int = 20, skip: int = 0) -> List[Dict[str, Any]]:
    """
    Получает список записей дневника конкретного пользователя.
    
    Args:
        user_id (str): ID пользователя
        limit (int, optional): Максимальное количество записей. По умолчанию 20.
        skip (int, optional): Количество записей для пропуска (для пагинации). По умолчанию 0.
        
    Returns:
        List[Dict[str, Any]]: Список записей
    """
    try:
        entries = await journal_entries_collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
        
        return entries
    
    except Exception as e:
        logger.error(f"Ошибка при получении записей дневника пользователя: {str(e)}")
        return []

async def update_journal_entry(entry_id: str, update_data: Dict[str, Any]) -> bool:
    """
    Обновляет запись дневника.
    
    Args:
        entry_id (str): ID записи
        update_data (Dict[str, Any]): Данные для обновления
        
    Returns:
        bool: True, если обновление успешно, иначе False
    """
    try:
        result = await journal_entries_collection.update_one(
            {"id": entry_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    except Exception as e:
        logger.error(f"Ошибка при обновлении записи дневника: {str(e)}")
        return False

async def delete_journal_entry(entry_id: str, user_id: str) -> bool:
    """
    Удаляет запись дневника.
    
    Args:
        entry_id (str): ID записи
        user_id (str): ID пользователя (для проверки доступа)
        
    Returns:
        bool: True, если удаление успешно, иначе False
    """
    try:
        # Проверяем, что запись принадлежит пользователю
        entry = await journal_entries_collection.find_one({"id": entry_id})
        if not entry or entry["user_id"] != user_id:
            return False
        
        result = await journal_entries_collection.delete_one({"id": entry_id})
        return result.deleted_count > 0
    
    except Exception as e:
        logger.error(f"Ошибка при удалении записи дневника: {str(e)}")
        return False

# Функции для работы с чатами
async def create_chat_session(session_data: Dict[str, Any]) -> str:
    """
    Создает новую сессию чата.
    
    Args:
        session_data (Dict[str, Any]): Данные сессии
        
    Returns:
        str: ID созданной сессии
    """
    try:
        # Добавляем даты создания и обновления, если их нет
        now = datetime.now()
        if "created_at" not in session_data:
            session_data["created_at"] = now
        if "updated_at" not in session_data:
            session_data["updated_at"] = now
        
        # Инициализируем пустой список сообщений, если его нет
        if "messages" not in session_data:
            session_data["messages"] = []
        
        # Вставляем сессию в базу
        result = await chat_sessions_collection.insert_one(session_data)
        return str(result.inserted_id)
    
    except Exception as e:
        logger.error(f"Ошибка при создании сессии чата: {str(e)}")
        raise

async def get_chat_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Получает сессию чата по ID.
    
    Args:
        session_id (str): ID сессии
        
    Returns:
        Optional[Dict[str, Any]]: Данные сессии или None, если сессия не найдена
    """
    try:
        session = await chat_sessions_collection.find_one({"id": session_id})
        return session
    
    except Exception as e:
        logger.error(f"Ошибка при получении сессии чата по ID: {str(e)}")
        return None

async def get_user_chat_sessions(user_id: str, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
    """
    Получает список сессий чата конкретного пользователя.
    
    Args:
        user_id (str): ID пользователя
        limit (int, optional): Максимальное количество сессий. По умолчанию 10.
        skip (int, optional): Количество сессий для пропуска (для пагинации). По умолчанию 0.
        
    Returns:
        List[Dict[str, Any]]: Список сессий
    """
    try:
        sessions = await chat_sessions_collection.find(
            {"user_id": user_id}
        ).sort("updated_at", -1).skip(skip).limit(limit).to_list(length=limit)
        
        return sessions
    
    except Exception as e:
        logger.error(f"Ошибка при получении сессий чата пользователя: {str(e)}")
        return []

async def add_message_to_chat(session_id: str, message: Dict[str, str]) -> bool:
    """
    Добавляет сообщение в сессию чата.
    
    Args:
        session_id (str): ID сессии
        message (Dict[str, str]): Сообщение в формате {"role": "user/assistant", "content": "text"}
        
    Returns:
        bool: True, если сообщение добавлено успешно, иначе False
    """
    try:
        result = await chat_sessions_collection.update_one(
            {"id": session_id},
            {
                "$push": {"messages": message},
                "$set": {"updated_at": datetime.now()}
            }
        )
        return result.modified_count > 0
    
    except Exception as e:
        logger.error(f"Ошибка при добавлении сообщения в чат: {str(e)}")
        return False

async def delete_chat_session(session_id: str, user_id: str) -> bool:
    """
    Удаляет сессию чата.
    
    Args:
        session_id (str): ID сессии
        user_id (str): ID пользователя (для проверки доступа)
        
    Returns:
        bool: True, если удаление успешно, иначе False
    """
    try:
        # Проверяем, что сессия принадлежит пользователю
        session = await chat_sessions_collection.find_one({"id": session_id})
        if not session or session["user_id"] != user_id:
            return False
        
        result = await chat_sessions_collection.delete_one({"id": session_id})
        return result.deleted_count > 0
    
    except Exception as e:
        logger.error(f"Ошибка при удалении сессии чата: {str(e)}")
        return False

# Функции для статистики и аналитики
async def get_user_emotion_stats(user_id: str, days: int = 30) -> Dict[str, Any]:
    """
    Получает статистику эмоций пользователя за указанный период.
    
    Args:
        user_id (str): ID пользователя
        days (int, optional): Количество дней для анализа. По умолчанию 30.
        
    Returns:
        Dict[str, Any]: Статистика эмоций
    """
    try:
        # Вычисляем дату начала периода
        start_date = datetime.now()
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = start_date.replace(day=start_date.day - days)
        
        # Получаем записи за указанный период
        entries = await journal_entries_collection.find({
            "user_id": user_id,
            "created_at": {"$gte": start_date}
        }).sort("created_at", 1).to_list(length=None)
        
        # Если нет записей, возвращаем пустую статистику
        if not entries:
            return {
                "period_days": days,
                "total_entries": 0,
                "emotion_trends": {},
                "dominant_emotions": []
            }
        
        # Обрабатываем статистику
        emotion_totals = {
            "радость": 0,
            "грусть": 0,
            "тревога": 0,
            "спокойствие": 0,
            "энергия": 0
        }
        
        dominant_emotions = {}
        
        for entry in entries:
            # Учитываем эмоции, если они есть
            if "emotions" in entry and entry["emotions"]:
                for emotion, value in entry["emotions"].items():
                    if emotion in emotion_totals:
                        emotion_totals[emotion] += value
            
            # Учитываем доминирующую эмоцию
            if "dominant_emotion" in entry and entry["dominant_emotion"]:
                dom_emotion = entry["dominant_emotion"]
                if dom_emotion in dominant_emotions:
                    dominant_emotions[dom_emotion] += 1
                else:
                    dominant_emotions[dom_emotion] = 1
        
        # Формируем результат
        dominant_emotions_list = [
            {"emotion": emotion, "count": count}
            for emotion, count in dominant_emotions.items()
        ]
        dominant_emotions_list.sort(key=lambda x: x["count"], reverse=True)
        
        return {
            "period_days": days,
            "total_entries": len(entries),
            "emotion_trends": emotion_totals,
            "dominant_emotions": dominant_emotions_list
        }
    
    except Exception as e:
        logger.error(f"Ошибка при получении статистики эмоций: {str(e)}")
        return {
            "period_days": days,
            "total_entries": 0,
            "emotion_trends": {},
            "dominant_emotions": [],
            "error": str(e)
        }
