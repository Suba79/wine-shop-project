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

def load_and_group_wines(filepath):
    try:
        df = pd.read_excel(filepath, engine='openpyxl')
        df = df.fillna('')
        
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
        
        return dict(grouped_wines)
    
    except FileNotFoundError:
        print(f"Файл {filepath} не найден")
        return {}
    except Exception as error:
        print(f"Ошибка при чтении файла: {error}")
        return {}

def main():
    print("\n" + "=" * 70)
    print("ЧИТАЕМ ФАЙЛ РОЗЫ: wine_catalog.xlsx")
    print("=" * 70)
    
    grouped_wines = load_and_group_wines('wine_catalog.xlsx')
    
    if grouped_wines:
        print(f"\nЗагружено категорий: {len(grouped_wines)}")
        
        total_wines = sum(len(wines) for wines in grouped_wines.values())
        print(f"Всего товаров: {total_wines}")
        
        special_count = sum(
            1 for wines in grouped_wines.values() 
            for wine in wines if wine['Выгодное предложение']
        )
        print(f"Товаров с акцией: {special_count}")
    
    print("=" * 70)
    
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

if __name__ == '__main__':
    main()