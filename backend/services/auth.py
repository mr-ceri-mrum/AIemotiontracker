"""
Сервис для аутентификации и авторизации пользователей.
Включает функции для хеширования паролей, создания и проверки JWT токенов.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Настройки для JWT
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")  # В продакшне должен быть в переменных окружения
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней

# Настройка контекста для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие обычного пароля хешированному.
    
    Args:
        plain_password (str): Обычный пароль
        hashed_password (str): Хешированный пароль
        
    Returns:
        bool: True, если пароль верный, иначе False
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Создает хеш пароля.
    
    Args:
        password (str): Пароль для хеширования
        
    Returns:
        str: Хешированный пароль
    """
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Создает JWT токен доступа.
    
    Args:
        data (Dict[str, Any]): Данные для включения в токен
        expires_delta (Optional[timedelta], optional): Срок действия токена. По умолчанию None.
        
    Returns:
        str: JWT токен
    """
    to_encode = data.copy()
    
    # Устанавливаем срок действия токена
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Создаем токен
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Декодирует JWT токен доступа.
    
    Args:
        token (str): JWT токен
        
    Returns:
        Optional[Dict[str, Any]]: Данные из токена или None, если токен недействителен
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"Ошибка при декодировании JWT токена: {str(e)}")
        return None

def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Извлекает ID пользователя из JWT токена.
    
    Args:
        token (str): JWT токен
        
    Returns:
        Optional[str]: ID пользователя или None, если токен недействителен
    """
    payload = decode_access_token(token)
    if payload and "sub" in payload:
        return payload["sub"]
    return None
