from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import pandas as pd
from collections import defaultdict

def pluralize_years(years):
    last_digit = years % 10
    last_two_digits = years % 100
    
    if 11 <= last_two_digits <= 14:
        return "лет"
    if last_digit == 1:
        return "год"
    if 2 <= last_digit <= 4:
        return "года"
    return "лет"


try:
    df = pd.read_excel('wine_catalog.xlsx', engine='openpyxl')
    df = df.fillna('')
    
    print(f"Загружено {len(df)} записей")
    print(f"Колонки: {list(df.columns)}")
    
    grouped_wines = defaultdict(list)
    
    for _, row in df.iterrows():
        has_special_offer = (row['Акция'] == 'Выгодное предложение')
        
        wine = {
            'Название': row['Название'],
            'Сорт': row['Сорт'],
            'Цена': row['Цена'],
            'Картинка': row['Картинка'],
            'Выгодное предложение': has_special_offer,
        }
        grouped_wines[row['Категория']].append(wine)
    
    print("\nТОВАРЫ С АКЦИЕЙ:")
    found_count = 0
    for category, wines in grouped_wines.items():
        for wine in wines:
            if wine['Выгодное предложение']:
                print(f"  {category}: {wine['Название']} - {wine['Цена']}р.")
                found_count += 1
    
    if found_count == 0:
        print("  Нет товаров с акцией")
    else:
        print(f"\nНайдено товаров с акцией: {found_count}")
    
    grouped_wines = dict(grouped_wines)
    
except FileNotFoundError:
    print(f"Файл wine3.xlsx не найден в папке проекта")
    grouped_wines = {}
except Exception as error:
    print(f"Ошибка при чтении файла: {error}")
    grouped_wines = {}


env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

env.globals['pluralize'] = pluralize_years
template = env.get_template('template.html')

current_year = datetime.now().year
founded_year = 1920
age = current_year - founded_year

rendered_page = template.render(
    age=age,
    grouped_wines=grouped_wines
)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)

server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
print(f"\nСайт доступен по адресу: http://127.0.0.1:8000/index.html")
print(f"Возраст винодельни: {age} {pluralize_years(age)}")
server.serve_forever()