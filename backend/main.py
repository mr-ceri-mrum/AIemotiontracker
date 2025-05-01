import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Body, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from openai import AsyncOpenAI
from dotenv import load_dotenv
import uuid
import logging

# Загрузка переменных окружения
load_dotenv()

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Инициализация FastAPI
app = FastAPI(title="AI Emotion Tracker API", version="1.0.0")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшне следует указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение к MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.emotion_tracker_db

# Инициализация OpenAI клиента
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Модели данных
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    created_at: datetime
    premium: bool = False
    
    class Config:
        from_attributes = True

class JournalEntry(BaseModel):
    id: Optional[str] = None
    user_id: str
    content: str
    created_at: Optional[datetime] = None
    emotions: Optional[Dict[str, float]] = None
    dominant_emotion: Optional[str] = None
    analysis: Optional[str] = None
    recommendations: Optional[str] = None

class EmotionResponse(BaseModel):
    emotions: Dict[str, float]
    dominant_emotion: str
    analysis: str
    recommendations: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatSession(BaseModel):
    id: Optional[str] = None
    user_id: str
    messages: List[Dict[str, str]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# OAuth2 для аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Зависимости
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # В продакшне здесь должна быть проверка токена JWT
    # Для примера используем упрощенную логику
    user = await db.users.find_one({"id": token})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректные учетные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return User(**user)

# Роуты для аутентификации
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # В продакшне здесь должна быть проверка хешированного пароля
    user = await db.users.find_one({"username": form_data.username})
    if not user or form_data.password != user.get("password"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user["id"], "token_type": "bearer"}

@app.post("/users", response_model=User)
async def create_user(user: UserCreate):
    # Проверка, что пользователь не существует
    existing_user = await db.users.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует",
        )
    
    # Создание нового пользователя
    new_user = User(
        id=str(uuid.uuid4()),
        username=user.username,
        email=user.email,
        created_at=datetime.now(),
        premium=False,
    )
    
    # В продакшне пароль должен быть хеширован
    user_dict = {**new_user.model_dump(), "password": user.password}
    await db.users.insert_one(user_dict)
    
    return new_user

# Роуты для работы с записями дневника
@app.post("/journal", response_model=JournalEntry)
async def create_journal_entry(
    entry: JournalEntry = Body(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user)
):
    # Проверка доступа
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на создание записи для другого пользователя",
        )
    
    # Устанавливаем ID и дату создания
    entry.id = str(uuid.uuid4())
    entry.created_at = datetime.now()
    
    # Сохраняем запись
    await db.journal_entries.insert_one(entry.model_dump())
    
    # Запускаем фоновую задачу для анализа эмоций
    background_tasks.add_task(analyze_emotion, entry.id)
    
    return entry

@app.get("/journal/{entry_id}", response_model=JournalEntry)
async def get_journal_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user)
):
    entry = await db.journal_entries.find_one({"id": entry_id})
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена",
        )
    
    # Проверка доступа
    if entry["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на просмотр этой записи",
        )
    
    return JournalEntry(**entry)

@app.get("/journal/user/{user_id}", response_model=List[JournalEntry])
async def get_user_journal_entries(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    # Проверка доступа
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на просмотр записей другого пользователя",
        )
    
    entries = await db.journal_entries.find({"user_id": user_id}).sort("created_at", -1).to_list(None)
    return [JournalEntry(**entry) for entry in entries]

# Роуты для работы с чатом
@app.post("/chat/session", response_model=ChatSession)
async def create_chat_session(
    user_id: str = Body(...),
    current_user: User = Depends(get_current_user)
):
    # Проверка доступа
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на создание сессии для другого пользователя",
        )
    
    # Создаем новую сессию чата
    now = datetime.now()
    session = ChatSession(
        id=str(uuid.uuid4()),
        user_id=user_id,
        messages=[],
        created_at=now,
        updated_at=now,
    )
    
    # Сохраняем сессию
    await db.chat_sessions.insert_one(session.model_dump())
    
    return session

@app.get("/chat/session/{session_id}", response_model=ChatSession)
async def get_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    session = await db.chat_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия не найдена",
        )
    
    # Проверка доступа
    if session["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на просмотр этой сессии",
        )
    
    return ChatSession(**session)

@app.post("/chat/session/{session_id}/message")
async def add_message_to_session(
    session_id: str,
    message: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_user)
):
    # Получаем сессию
    session = await db.chat_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия не найдена",
        )
    
    # Проверка доступа
    if session["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на отправку сообщений в эту сессию",
        )
    
    # Добавляем сообщение пользователя
    session["messages"].append({"role": "user", "content": message["content"]})
    
    # Получаем ответ от OpenAI
    messages = session["messages"]
    
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o",  # Используем современную модель
            messages=messages,
            max_tokens=500,
        )
        assistant_message = response.choices[0].message.content
        
        # Добавляем ответ ассистента
        assistant_message_obj = {"role": "assistant", "content": assistant_message}
        session["messages"].append(assistant_message_obj)
        
        # Обновляем сессию в базе данных
        session["updated_at"] = datetime.now()
        await db.chat_sessions.update_one(
            {"id": session_id},
            {"$set": {
                "messages": session["messages"],
                "updated_at": session["updated_at"]
            }}
        )
        
        return {"message": "Сообщение добавлено", "assistant_response": assistant_message}
    
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке запроса: {str(e)}",
        )

@app.get("/chat/sessions/user/{user_id}", response_model=List[ChatSession])
async def get_user_chat_sessions(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    # Проверка доступа
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на просмотр сессий другого пользователя",
        )
    
    sessions = await db.chat_sessions.find({"user_id": user_id}).sort("updated_at", -1).to_list(None)
    return [ChatSession(**session) for session in sessions]

# Функция для анализа эмоций с помощью OpenAI
async def analyze_emotion(entry_id: str):
    try:
        # Получаем запись
        entry = await db.journal_entries.find_one({"id": entry_id})
        if not entry:
            logger.error(f"Запись с ID {entry_id} не найдена")
            return
        
        # Запрос к OpenAI для анализа эмоций
        system_prompt = """
        Ты - эксперт по анализу эмоций. Проанализируй текст и определи эмоциональное состояние автора. 
        Выдели основные эмоции и их интенсивность по шкале от 0 до 100. 
        Определи доминирующую эмоцию.
        Дай краткое описание эмоционального состояния автора и рекомендации для улучшения ментального благополучия.
        
        Верни результат в формате JSON:
        {
            "emotions": {
                "радость": число,
                "грусть": число,
                "тревога": число,
                "спокойствие": число,
                "энергия": число
            },
            "dominant_emotion": "название эмоции",
            "analysis": "анализ эмоционального состояния",
            "recommendations": "рекомендации"
        }
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": entry["content"]}
        ]
        
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"},
        )
        
        result = response.choices[0].message.content
        import json
        analysis_data = json.loads(result)
        
        # Обновляем запись с результатами анализа
        await db.journal_entries.update_one(
            {"id": entry_id},
            {"$set": {
                "emotions": analysis_data["emotions"],
                "dominant_emotion": analysis_data["dominant_emotion"],
                "analysis": analysis_data["analysis"],
                "recommendations": analysis_data["recommendations"]
            }}
        )
        
        logger.info(f"Анализ эмоций для записи {entry_id} успешно завершен")
    
    except Exception as e:
        logger.error(f"Ошибка при анализе эмоций: {str(e)}")

# Запуск с помощью uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
