import requests
from bs4 import BeautifulSoup
import shutil  # save img locally


def save_img(url, file_name):
    res = requests.get(url, stream=True)

    if res.status_code == 200:
        with open(f"./media/product/{file_name}.jpg", "wb") as f:
            shutil.copyfileobj(res.raw, f)
        print("Image sucessfully Downloaded: ", file_name)
    else:
        print("Image Couldn't be retrieved")


target_urls = [
    "https://www.muztorg.ru/category/dj-oborudovanie/",
    "https://www.muztorg.ru/category/naushniki-i-garnitury",
    "https://www.muztorg.ru/category/svetovoe-oborudovanie",
    "https://www.muztorg.ru/category/zvukovoe-oborudovanie",
    "https://www.muztorg.ru/category/smychkovye-instrumenty",
    "https://www.muztorg.ru/category/duhovye-instrumenty",
    "https://www.muztorg.ru/category/mikrofony-i-radiosistemy",
    "https://www.muztorg.ru/category/gitary",
]

# for url in target_urls:
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, "html.parser")
#     for link in soup.find_all("div", class_="category"):
#         print(link.get("href"))


response = requests.get("https://www.muztorg.ru/category/dj-oborudovanie/")
soup = BeautifulSoup(response.text, "lxml")
subcategories_urls = [
    "https://www.muztorg.ru" + link.get("href")
    for link in soup.find_all("a", class_="category")
]
print(subcategories_urls)
for url in subcategories_urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    for section in soup.find_all("section", class_="product-thumbnail"):
        current_section = section.find("meta", itemprop="url")
        if current_section:
            product_url = "https://www.muztorg.ru" + current_section.get("content")
            response = requests.get(product_url)
            soup = BeautifulSoup(response.text, "lxml")

            prod_category = soup.find_all("span", class_="product-category")[
                0
            ].text.strip()
            prod_title = soup.find_all("h1", class_="product-title")[0].text.strip()

            prod_price = soup.find_all("p", class_="price-value")[0].text.strip()
            prod_price = "".join([number for number in prod_price if number.isdigit()])

            prod_vendor_code = soup.find_all("span", itemprop="sku")[0].text.strip()
            prod_img_url = soup.find_all("img", id="slide1")[0].get("data-src")

            prod_short_description = soup.find_all("div", itemprop="description")[
                0
            ].text.strip()

            # p_tags = soup.find_all("div", role="tabpanel")
            # # characteristic = soup.find_all(
            # #     "div", role="tabpanel", class_="tab-pane fade active in"
            # # )[1]

            # print(p_tags[0])

            # prod_description = p_tags[0].text
            save_img(prod_img_url, prod_vendor_code)
            print(
                prod_category,
                prod_title,
                prod_vendor_code,
                prod_price,
                prod_short_description,
                prod_description,
                prod_img_url,
                sep="|",
            )
