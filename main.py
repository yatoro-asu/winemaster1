import argparse
import os
from datetime import date
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from read_wines import load_product_categories

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_NAME = 'template.html'
OUTPUT_PATH = BASE_DIR / 'index.html'
WINERY_FOUNDING_YEAR = 1920
DEFAULT_DATA_FILE = BASE_DIR / 'data' / 'wine3.xlsx'


def decline_year(years: int) -> str:
    if years % 100 in (11, 12, 13, 14):
        return 'лет'

    last_digit = years % 10
    if last_digit == 1:
        return 'год'
    if last_digit in (2, 3, 4):
        return 'года'
    return 'лет'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Запуск статического сервера для сайта с вином.'
    )
    parser.add_argument(
        '--data-file',
        default=os.getenv('WINE_DATA_FILE', str(DEFAULT_DATA_FILE)),
        help='Путь к Excel-файлу с данными о вине.',
    )
    return parser.parse_args()


def create_index_html(data_path: Path) -> None:
    current_year = date.today().year
    winery_age = current_year - WINERY_FOUNDING_YEAR
    product_categories = load_product_categories(data_path)

    env = Environment(loader=FileSystemLoader(str(BASE_DIR)), autoescape=True)
    template = env.get_template(TEMPLATE_NAME)
    rendered = template.render(
        winery_age=winery_age,
        current_year=current_year,
        decline_year=decline_year,
        product_categories=product_categories,
    )

    OUTPUT_PATH.write_text(rendered, encoding='utf-8')
    print(f'Created {OUTPUT_PATH}')


def main() -> None:
    args = parse_args()
    create_index_html(Path(args.data_file))

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    print('Serving at http://127.0.0.1:8000')
    server.serve_forever()


if __name__ == '__main__':
    main()
