import sqlite3
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment

DB_PATH = "northwind.db"

SUMMARY_QUERY = '''
SELECT
    c.CompanyName,
    c.Country,
    COUNT(o.OrderID) AS order_count,
    ROUND(SUM(o.Freight),2) AS total_freight
FROM Customers AS c
JOIN Orders AS o ON c.CustomerID = o.CustomerID
GROUP BY c.CustomerID, c.CompanyName, c.Country
ORDER BY total_freight DESC
'''

def fetch_summary():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(SUMMARY_QUERY, conn)
    conn.close()
    return df

def save_to_excel(df):
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"report_{date_str}.xlsx"
    df.to_excel(filename, index=False, engine="openpyxl")
    print(f"Отчёт сохранён: {filename}")
    return filename

def format_excel(filename):
    wb = load_workbook(filename)
    ws = wb.active

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    thin = Side(style="thin", color="B0B0B0")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.border = border
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.border = border

    for column_cells in ws.columns:
        max_length = max(len(str(cell.value)) if cell.value is not None else 0
                         for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = max_length + 4

    ws.freeze_panes = "A2"
    wb.save(filename)
    print(f"Форматирование применено: {filename}")

if __name__ == "__main__":
    df = fetch_summary()
    print(f"Строк в отчёте: {len(df)}")
    filename = save_to_excel(df)
    format_excel(filename)