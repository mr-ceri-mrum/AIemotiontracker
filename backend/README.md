# AI Дневник Эмоций - Backend API

Бэкенд API для приложения "AI Дневник Эмоций" на Python 3.13 с использованием FastAPI, MongoDB и OpenAI API.

## Описание

Этот бэкенд предоставляет API для приложения AI Дневник Эмоций, включающий:

- Аутентификацию и управление пользователями
- Сохранение и анализ дневниковых записей
- Анализ эмоций с использованием OpenAI API
- Чат-сессии с сохранением контекста
- Статистику и аналитику эмоционального состояния

## Требования

- Python 3.13 или выше
- MongoDB
- OpenAI API ключ

## Установка и запуск

1. Клонировать репозиторий:
```bash
git clone https://github.com/mr-ceri-mrum/AIemotiontracker.git
cd AIemotiontracker/backend
```

2. Создать и активировать виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. Установить зависимости:
```bash
pip install -r requirements.txt
```

4. Создать файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

5. Отредактировать файл `.env` и добавить свой API ключ OpenAI и другие настройки:
```
OPENAI_API_KEY=your_openai_api_key_here
MONGO_URL=mongodb://localhost:27017
```

6. Запустить сервер:
```bash
uvicorn main:app --reload
```

Сервер будет доступен по адресу http://localhost:8000

## API Endpoints

### Аутентификация

- `POST /token` - Получение токена доступа
- `POST /users` - Регистрация нового пользователя

### Дневник эмоций

- `POST /journal` - Создание новой записи
- `GET /journal/{entry_id}` - Получение конкретной записи
- `GET /journal/user/{user_id}` - Получение списка записей пользователя

### Чат

- `POST /chat/session` - Создание новой сессии чата
- `GET /chat/session/{session_id}` - Получение конкретной сессии
- `POST /chat/session/{session_id}/message` - Добавление сообщения в сессию
- `GET /chat/sessions/user/{user_id}` - Получение списка сессий пользователя

## Документация API

После запуска сервера, документация OpenAPI (Swagger) доступна по адресу:
http://localhost:8000/docs

## Интеграция с OpenAI

Бэкенд использует OpenAI API для:

1. Анализа эмоционального состояния пользователя на основе текста
2. Генерации персонализированных рекомендаций для улучшения ментального здоровья
3. Создания диалогового интерфейса с сохранением контекста чата

## Структура проекта

```
backend/
├── main.py                     # Основной файл FastAPI приложения
├── models.py                   # Модели данных Pydantic
├── requirements.txt            # Зависимости проекта
├── .env.example                # Пример файла конфигурации
└── services/                   # Сервисные модули
    ├── __init__.py             # Инициализация пакета services
    ├── auth.py                 # Сервис аутентификации
    ├── database.py             # Сервис для работы с базой данных
    └── openai_service.py       # Сервис для работы с OpenAI API
```