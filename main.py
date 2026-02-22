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

def main():
    df = pd.read_excel('wine_catalog.xlsx', engine='openpyxl')
    df = df.fillna('')
    
    grouped_wines = defaultdict(list)
    
    for _, row in df.iterrows():
        wine = {
            'Название': row['Название'],
            'Сорт': row['Сорт'],
            'Цена': row['Цена'],
            'Картинка': row['Картинка'],
            'Выгодное предложение': (row['Акция'] == 'Выгодное предложение'),
        }
        grouped_wines[row['Категория']].append(wine)
    
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    env.globals['pluralize'] = pluralize_years
    template = env.get_template('template.html')
    
    current_year = datetime.now().year
    age = current_year - 1920
    
    rendered_page = template.render(
        age=age,
        grouped_wines=dict(grouped_wines)
    )
    
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    
    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    print(f"Сайт: http://127.0.0.1:8000/index.html")
    print(f"Возраст: {age} {pluralize_years(age)}")
    server.serve_forever()

if __name__ == '__main__':
    main()