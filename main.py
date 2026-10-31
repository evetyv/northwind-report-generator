import sqlite3
import pandas as pd
from llm_sql import text_to_sql, get_schema_description
from report_generator import save_to_excel, format_excel

DB_PATH = "northwind.db"


def run_query(sql: str):
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(sql, conn)
        return df
    finally:
        conn.close()


def main():
    print("=== Доступные таблицы ===")
    print(get_schema_description())
    print()

    question = input("Введите запрос словами: ").strip()
    if not question:
        print("Пустой запрос, выходим.")
        return

    print("\nГенерирую SQL...")
    sql = text_to_sql(question)

    print("\n=== Сгенерированный SQL ===")
    print(sql)
    print()

    confirm = input("Выполнить (y), редактировать (e) или отменить (n)? ").strip().lower()

    if confirm == "n":
        print("Отменено.")
        return
    elif confirm == "e":
        print("\nОткрой SQL для правки. Введи исправленный запрос одной строкой.")
        print("(Enter без текста — оставить как было)")
        edited = input("SQL> ").strip()
        if edited:
            sql = edited
        print("\n=== Итоговый SQL ===")
        print(sql)
        print()
    elif confirm != "y":
        print("Неизвестная команда, отменено.")
        return

    print("\nВыполняю...")
    try:
        df = run_query(sql)
    except Exception as e:
        print(f"Ошибка при выполнении SQL: {e}")
        return

    print(f"Получено строк: {len(df)}")
    print(df.head())

    filename = save_to_excel(df)
    format_excel(filename)
    print("Готово.")


if __name__ == "__main__":
    main()