# -*- coding: utf8 -*-

import requests
from bs4 import BeautifulSoup
import csv

HOST = 'https://fix-price.ru'
url_request = 'https://fix-price.ru/personal/'
url_auth = 'https://fix-price.ru/ajax/auth_user.php'
FILE_info = 'info.csv'
FILE_products = 'product.csv'

HEADERS = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'referer': 'https://fix-price.ru/personal/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    'x-kl-ajax-request': 'Ajax_Request'
}

session = requests.Session()
session.headers.update(HEADERS)
r_csrf = session.get(url_request)
soup_csrf = BeautifulSoup(r_csrf.content, 'html.parser')
csrf = soup_csrf.find('input', {'name': 'CSRF'})['value']

# phone = '+7 (920) 156-05-96'
# password = 'Fixprice123'

phone = input('Login: ')
password = input('Password: ')

data = {
    'AUTH_FORM': 'Y',
    'TYPE': 'AUTH',
    'CSRF': csrf,
    'backurl': '/personal/',
    'auth_method': 'phone',
    'login': phone,
    'password': password,
}

response = session.post(url_auth, data=data)


def get_html(url, params=None):
    r = session.get(url, headers=HEADERS, params=params)
    return r


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='main-list__card-item')
    profiles = soup.find_all('div', class_='bx-auth-profile')

    info = []
    for profile in profiles:
        gender_mas = profile.find('input', {'name': 'PERSONAL_GENDER'})['value'],
        gender = gender_mas[0]
        if gender == 'F':
            gender = 'Женский'
        else:
            gender = 'Мужской'
        info.append({
            'last_name': profile.find('input', {'name': 'LAST_NAME'})['value'],
            'name': profile.find('input', {'name': 'NAME'})['value'],
            'second_name': profile.find('input', {'name': 'SECOND_NAME'})['value'],
            'email': profile.find('input', class_='email-now')['value'],
            'date': profile.find('input', {'name': 'PERSONAL_BIRTHDAY'})['value'],
            'gender': gender,
            'card': profile.find('div', class_='personal-card__number').get_text()
        })

    products = []
    for item in items:

        available = item.find('span', class_='product-card__bottom-btn')
        if available:
            available = 'Доступно для заказа в интернет-магазине'
        else:
            available = 'Доступно только в магазинах'

        popular = item.find('div', class_='product-card__badge')
        if popular:
            popular = 'Хит'
        else:
            popular = ''

        products.append({
            'title': item.find('a', class_='product-card__title').get_text(strip=True),
            'link': HOST + item.find('a', class_='product-card__title').get('href'),
            'price': item.find('span', class_='badge-price-value').find_next('span').get_text(),
            'available': available,
            'popular': popular
        })
    # print(info)
    # print(products)
    print('Процесс запущен...')
    save_profile(info, FILE_info)
    save_product(products, FILE_products)


def save_profile(profiles, path):
    with open(path, 'w', newline='') as file:
        writer_info = csv.writer(file, delimiter=';')
        writer_info.writerow(['Фамилия', 'Имя', 'Отчество', 'Email', 'Дата Рождения', 'Пол', 'Номер карты'])
        for profile in profiles:
            writer_info.writerow(
                [profile['last_name'], profile['name'], profile['second_name'], profile['email'], profile['date'],
                 profile['gender'], profile['card']])


def save_product(items, path):
    with open(path, 'w', newline='') as file:
        writer_products = csv.writer(file, delimiter=';')
        writer_products.writerow(['Название', 'Ссылка', 'Цена', 'Доступность для заказа', 'Тип'])
        for item in items:
            writer_products.writerow([item['title'], item['link'], item['price'], item['available'], item['popular']])


def parse():
    for URL in [
        'https://fix-price.ru/personal/#favorites',
        'https://fix-price.ru/personal/#profile'
    ]:
        html = get_html(URL)
        if html.status_code == 200:
            get_content(html.text)
            print('Готово')
        else:
            print('Error')


parse()
