import time
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def dns_search_uc(query: str, limit: int = 5, timeout: int = 50):
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1366,768")

    results = []

    with uc.Chrome(options=options) as driver:

        driver.get("https://www.dns-shop.ru/")
        time.sleep(1.5)


        driver.get(f"https://www.dns-shop.ru/search/?q={query}")
        WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".catalog-product, .product"))
        )
        time.sleep(1.0)

        html = driver.page_source


    soup = BeautifulSoup(html, "lxml")
    for card in soup.select(".catalog-product, .product"):
        title_el = card.select_one("a.catalog-product__name, .product-info__title-link a, a.ui-link")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        href = title_el.get("href") or "#"
        url = "https://www.dns-shop.ru" + href if href.startswith("/") else href

        price_el = (
            card.select_one(".product-buy__price") or
            card.select_one(".product-buy__cur-price") or
            card.select_one(".product-card__price") or
            card.select_one("[class*='price']")
        )
        price = price_el.get_text(strip=True) if price_el else "цена не найдена"

        results.append((title, price, url))
        if len(results) >= limit:
            break

    return results

# [(), (), (), (), ()]




