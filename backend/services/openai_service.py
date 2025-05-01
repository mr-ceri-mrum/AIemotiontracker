"""
Сервис для работы с OpenAI API.
Включает функции для анализа эмоций и обработки сообщений чата.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Инициализация клиента OpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def analyze_emotions(text: str) -> Dict[str, Any]:
    """
    Анализирует эмоциональное состояние на основе текста пользователя.
    
    Args:
        text (str): Текст для анализа
        
    Returns:
        Dict[str, Any]: Словарь с результатами анализа эмоций
    """
    try:
        system_prompt = """
        Ты - эксперт по анализу эмоций и психологическому благополучию. 
        Проанализируй текст и определи эмоциональное состояние автора. 
        Выдели пять основных эмоций и их интенсивность по шкале от 0 до 100:
        - радость
        - грусть
        - тревога
        - спокойствие
        - энергия
        
        Определи доминирующую эмоцию или сочетание двух главных эмоций.
        Дай краткое описание эмоционального состояния автора (2-3 предложения).
        Предложи 1-2 конкретные рекомендации для улучшения ментального благополучия.
        
        Верни результат строго в формате JSON:
        {
            "emotions": {
                "радость": число,
                "грусть": число,
                "тревога": число,
                "спокойствие": число,
                "энергия": число
            },
            "dominant_emotion": "название эмоции или сочетания",
            "analysis": "анализ эмоционального состояния",
            "recommendations": "рекомендации"
        }
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
        # Получаем и парсим результат
        result = response.choices[0].message.content
        analysis_data = json.loads(result)
        
        # Проверяем, что результат содержит все необходимые поля
        required_fields = ["emotions", "dominant_emotion", "analysis", "recommendations"]
        missing_fields = [field for field in required_fields if field not in analysis_data]
        
        if missing_fields:
            logger.warning(f"В результате анализа отсутствуют поля: {', '.join(missing_fields)}")
            # Добавляем отсутствующие поля с пустыми значениями
            for field in missing_fields:
                if field == "emotions":
                    analysis_data[field] = {"радость": 0, "грусть": 0, "тревога": 0, "спокойствие": 0, "энергия": 0}
                else:
                    analysis_data[field] = "Информация недоступна"
        
        return analysis_data
    
    except Exception as e:
        logger.error(f"Ошибка при анализе эмоций: {str(e)}")
        # Возвращаем заглушку в случае ошибки
        return {
            "emotions": {"радость": 0, "грусть": 0, "тревога": 0, "спокойствие": 0, "энергия": 0},
            "dominant_emotion": "Не удалось определить",
            "analysis": "Не удалось проанализировать текст из-за ошибки",
            "recommendations": "Попробуйте повторить запрос позже"
        }

async def get_chat_response(
    messages: List[Dict[str, str]], 
    user_profile: Optional[Dict[str, Any]] = None,
    emotion_history: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Получает ответ от OpenAI на основе истории сообщений и контекста пользователя.
    
    Args:
        messages (List[Dict[str, str]]): История сообщений в формате [{"role": "user/assistant", "content": "text"}]
        user_profile (Optional[Dict[str, Any]]): Профиль пользователя с дополнительной информацией
        emotion_history (Optional[List[Dict[str, Any]]]): История эмоциональных состояний пользователя
        
    Returns:
        str: Ответ от ИИ
    """
    try:
        # Создаем системную инструкцию с учетом профиля и истории эмоций
        system_message = """
        Ты - эмпатичный и поддерживающий ассистент по ментальному здоровью и эмоциональному благополучию.
        Твоя задача - помогать пользователю отслеживать свое эмоциональное состояние, 
        давать поддерживающие комментарии и практические рекомендации для улучшения самочувствия.
        
        Отвечай с теплотой и пониманием. Избегай клинических или формальных фраз, 
        общайся как заботливый друг с психологическим образованием.
        
        Твои ответы должны быть краткими (2-4 предложения), конкретными и практически полезными.
        """
        
        # Если есть история эмоций, добавляем ее в системный промт
        if emotion_history and len(emotion_history) > 0:
            recent_emotions = emotion_history[:3]  # Берем только 3 последних состояния
            emotions_info = "\n\nИстория эмоциональных состояний пользователя:\n"
            
            for i, entry in enumerate(recent_emotions):
                date = entry.get("date", "Недавно")
                emotion = entry.get("dominant_emotion", "Не определено")
                emotions_info += f"{i+1}. {date}: {emotion}\n"
            
            system_message += emotions_info
        
        # Если есть профиль пользователя, добавляем информацию о премиум-статусе
        if user_profile and user_profile.get("premium"):
            system_message += "\n\nЭто премиум-пользователь, давай ему расширенные и более персонализированные рекомендации."
        
        # Формируем полный набор сообщений
        full_messages = [{"role": "system", "content": system_message}]
        full_messages.extend(messages)
        
        # Отправляем запрос к OpenAI
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=full_messages,
            temperature=0.8,
            max_tokens=500,
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        logger.error(f"Ошибка при получении ответа от OpenAI: {str(e)}")
        return "Извините, произошла ошибка при обработке вашего сообщения. Пожалуйста, попробуйте еще раз позже."
