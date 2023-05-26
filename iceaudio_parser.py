from bs4 import BeautifulSoup
from selenium import webdriver  # Для создания своего браузера
from selenium.webdriver.chrome.service import Service  # Для настройки Chrome
from selenium.webdriver.common.by import By  # Для указания способа которым будем искать элемент
from selenium.webdriver.common.keys import Keys  # Для работы с кнопками
import openpyxl

options_chrome = webdriver.ChromeOptions()
options_chrome.add_argument('headless')  # 2 Опции для работы браузера в фоновом режиме
service = Service(executable_path="driver_chrome/chromedriver.exe")  # Настройки браузера
browser = webdriver.Chrome(service=service, options=options_chrome)  # Запуск браузера

# Параметры для работы с Excel
wb = openpyxl.Workbook()
ws = wb.active
ws.append(['Product_id', 'Title', 'Price', 'Description', 'Image_url'])

url = 'https://iceaudio.no/'


# ЭТАП 1 - получение всех ссылок с товарами по категориям
def get_links():
    browser.get(url)  # Открытие страницы с url
    soup = BeautifulSoup(browser.page_source, 'lxml')  # Создание обертки
    lst_li = soup.find("ul", class_="treeview").find_all("li")  # Отбираю все элементы с тегом li
    # ul = browser.find_element(By.CLASS_NAME, "treeview").find_elements()  # тоже самое что и lst_li

    # Пробегаю по списку элементов с тегом li
    for i in lst_li:
        links = url + i.find('a').get('href')  # Отбор всех ссылок с нормальным видом
        if '&ID' in links:  # Отбор нужных мне ссылок
            yield links


# print(get_links())

# ЭТАП 2 - получение ссылок со всеми товарами в каждой категории
list_links_products = []  # переменная для нового списка с href всех товаров на каждой из страниц
for new_links in get_links():
    browser.get(new_links)  # запрос на каждую страницу new_links из списка list_links
    browser.implicitly_wait(3)
    soup = BeautifulSoup(browser.page_source, 'lxml')  # запрос на каждую страницу new_links из списка list_links
    items = soup.find("div", id="sub_content").find_all("div", class_="boxVareliste effect1")  # Отбор всех карточек
    for elm in items:
        all_hrefs = url + elm.find("tr").find("a", class_="borderit").get("href")
        # print("Количество товаров:", len(all_hrefs))
        list_links_products.append(all_hrefs)  # добавление ссылок в новый список
# print("Найдено всего товаров:", len(list_links_products))

# ЭТАП 3 - получение необходимой информации из каждого товара и сохранение в Excel
for links_products in list_links_products:
    browser.get(links_products)
    browser.implicitly_wait(3)  # вместо sleep
    soup = BeautifulSoup(browser.page_source, 'lxml')
    card = soup.find("div", id="PInfo")
    # забираем нужные нам сведения из каждой карточки товара
    product_id = card.find("div", id="PInfo_Right").find("tbody").text.split()[2]
    title = card.find("div", id="PInfo_Top").text.replace('\n', '').strip()
    price = card.find("div", id="PInfo_Right").text.splitlines()[14]
    description = card.find("div", id="PInfo_Right").text.replace('\n', '').replace('\xa0', '; ')
    image_url = url + card.find("div", id="PInfo_Left").find("img").get("src")
    data = {'product_id': product_id,
            'title': title,
            'price': price,
            'image': image_url,
            'description': description}
    # Добавление данных и запись в таблицу Excel
    ws.append([data['product_id'], data['title'], data['price'], data['description'], data['image']])
    wb.save('iceaudio_no.xlsx')
