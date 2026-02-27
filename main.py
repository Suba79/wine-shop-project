from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import pandas as pd
from collections import defaultdict
import argparse

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

def main():
    parser = argparse.ArgumentParser(description='Генератор сайта винодельни')
    parser.add_argument(
        '--data-path',
        type=str,
        default='wine_catalog.xlsx',
        help='Путь к Excel-файлу с данными о винах'
    )
    args = parser.parse_args()
    
    df = pd.read_excel(args.data_path, engine='openpyxl')
    df = df.fillna('')
    
    grouped_wines = defaultdict(list)
    
    for _, row in df.iterrows():
        is_special = (row['Акция'] == 'Выгодное предложение')
        
        wine = {
            'name': row['Название'],
            'grape': row['Сорт'],
            'price': row['Цена'],
            'image': row['Картинка'],
            'is_special': is_special,
        }
        grouped_wines[row['Категория']].append(wine)
    
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    env.globals['pluralize'] = pluralize_years
    template = env.get_template('template.html')
    
    FOUNDATION_YEAR = 1920
    current_year = datetime.now().year
    age = current_year - FOUNDATION_YEAR
    
    rendered_page = template.render(
        age=age,
        grouped_wines=grouped_wines
    )
    
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    
    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    print(f"Сайт: http://127.0.0.1:8000/index.html")
    print(f"Возраст: {age} {pluralize_years(age)}")
    print(f"Данные: {args.data_path}")
    server.serve_forever()

if __name__ == '__main__':
    main()