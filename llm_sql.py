import os
import sqlite3
from gigachat import GigaChat
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "northwind.db"

SYSTEM_PROMPT = """Ты — эксперт по SQL. Твоя задача — преобразовать вопрос пользователя в SQL-запрос для SQLite.
Используй только таблицы и колонки из предоставленной схемы, имена таблиц с пробелами заключай в двойные кавычки. Не выдумывай названия. Если имя таблицы или колонки содержит пробел (например, "Order Details"), 
обязательно заключай его в двойные кавычки.
Верни ТОЛЬКО текст SQL-запроса, без пояснений, без markdown-разметки (без ```sql).
Запрос должен начинаться с SELECT."""


def get_schema_description(db_path: str = DB_PATH) -> str:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    lines = []
    for table in tables:
        cursor.execute(f'PRAGMA table_info("{table}")')
        columns = cursor.fetchall()
        col_descriptions = ", ".join(f"{col[1]} ({col[2]})" for col in columns)
        lines.append(f"- {table}: {col_descriptions}")

    conn.close()
    return "\n".join(lines)


def text_to_sql(user_question: str) -> str:
    credentials = os.getenv("GIGACHAT_CREDENTIALS")
    if not credentials:
        raise ValueError("Не задана переменная окружения GIGACHAT_CREDENTIALS")

    schema = get_schema_description()

    with GigaChat(credentials=credentials, verify_ssl_certs=False, model="GigaChat-2") as client:
        prompt = f"{SYSTEM_PROMPT}\n\nСхема базы:\n{schema}\n\nВопрос пользователя: {user_question}"
        response = client.chat(prompt)
        return response.choices[0].message.content.strip()