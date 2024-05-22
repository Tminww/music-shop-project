import requests
from bs4 import BeautifulSoup
import shutil  # save img locally
import psycopg2
from datetime import datetime

from config import settings

conn = psycopg2.connect(
    database=settings.DB_NAME,
    user=settings.DB_USER,
    password=settings.DB_PASS,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
)
print(conn)


def insert_data_in_db(title, slug, short_description, sku, category_id, price):
    # transaction 1
    with conn:
        with conn.cursor() as cur:
            product_image = f"product/{sku}.jpg"
            stmt = "INSERT INTO store_product (title, slug, short_description, product_image, category_id, price, is_active, is_featured, created_at, updated_at, sku) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"
            # args = ",".join(cur.mogrify("%s, %s, %s"))
            cur.execute(
                stmt,
                (
                    title,
                    slug,
                    short_description,
                    product_image,
                    category_id,
                    price,
                    True,
                    True,
                    datetime.now(),
                    datetime.now(),
                    sku,
                ),
            )
            conn.commit()


def save_img(url, file_name):
    res = requests.get(url, stream=True)

    if res.status_code == 200:
        with open(f"./media/product/{file_name}.jpg", "wb") as f:
            shutil.copyfileobj(res.raw, f)
        print("Image sucessfully Downloaded: ", file_name)
    else:
        print("Image Couldn't be retrieved")


target_urls = [
    # (5, "https://www.muztorg.ru/category/narodnye-i-etnicheskie"),
    (4, "https://www.muztorg.ru/category/dj-oborudovanie/"),
    (2, "https://www.muztorg.ru/category/naushniki-i-garnitury"),
    (1, "https://www.muztorg.ru/category/svetovoe-oborudovanie"),
    (3, "https://www.muztorg.ru/category/zvukovoe-oborudovanie"),
    (6, "https://www.muztorg.ru/category/smychkovye-instrumenty"),
    (9, "https://www.muztorg.ru/category/duhovye-instrumenty"),
    (8, "https://www.muztorg.ru/category/mikrofony-i-radiosistemy"),
    (7, "https://www.muztorg.ru/category/gitary"),
]

for category_id, url in target_urls:
    print(category_id, url)
    response = requests.get(url)
    print(response.status_code)

    soup = BeautifulSoup(response.text, "lxml")
    subcategories_urls = [
        "https://www.muztorg.ru" + link.get("href")
        for link in soup.find_all("a", class_="category")
    ]
    print(subcategories_urls)
    for url in subcategories_urls:
        print(url)
        response = requests.get(url)
        print(response.status_code)
        soup = BeautifulSoup(response.text, "html.parser")
        for count, section in enumerate(
            soup.find_all("section", class_="product-thumbnail")
        ):
            current_section = section.find("meta", itemprop="url")
            if current_section and count < 4:
                product_url = "https://www.muztorg.ru" + current_section.get("content")
                response = requests.get(product_url)
                soup = BeautifulSoup(response.text, "lxml")

                prod_category = soup.find_all("span", class_="product-category")[
                    0
                ].text.strip()

                prod_title = soup.find_all("h1", class_="product-title")[0].text.strip()
                try:

                    prod_price = soup.find_all("p", class_="price-value")[
                        0
                    ].text.strip()
                    prod_price = "".join(
                        [number for number in prod_price if number.isdigit()]
                    )
                except:
                    prod_price = 12850

                prod_vendor_code = soup.find_all("span", itemprop="sku")[0].text.strip()
                try:
                    prod_img_url = soup.find_all("img", id="slide1")[0].get("data-src")
                except Exception as ex:
                    print(ex)
                prod_short_description = soup.find_all("div", itemprop="description")[
                    0
                ].text.strip()

                save_img(prod_img_url, prod_vendor_code)
                insert_data_in_db(
                    prod_title,
                    prod_category,
                    prod_short_description,
                    prod_vendor_code,
                    category_id,
                    prod_price,
                )
                print("Done!")
