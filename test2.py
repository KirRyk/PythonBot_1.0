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
    # Добавляем Headless для Render.com (без GUI)
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")

    results = []

    try:
        with uc.Chrome(options=options) as driver:
            driver.get(f"https://www.dns-shop.ru/search/?q={query}")

            # Ждем загрузки товаров
            WebDriverWait(driver, timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".catalog-product, .product"))
            )
            time.sleep(2.0)

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
            price = price_el.get_text(strip=True) if price_el else "Цена не указана"

            results.append({
                "title": title,
                "price": price,
                "url": url
            })

            if len(results) >= limit:
                break

        return results

    except Exception as e:
        return [{"error": f"Ошибка при поиске: {str(e)}"}]


# Функция для форматирования результатов в текст для Telegram
def format_results_for_telegram(results, query):
    if not results:
        return f"❌ По запросу '{query}' ничего не найдено."

    if isinstance(results, list) and results and "error" in results[0]:
        return f"⚠️ {results[0]['error']}"

    formatted = f"🔍 *Результаты поиска по запросу: {query}*\n\n"

    for i, item in enumerate(results, 1):
        formatted += f"{i}. *{item['title']}*\n"
        formatted += f"   💰 Цена: {item['price']}\n"
        formatted += f"   🔗 [Ссылка на товар]({item['url']})\n\n"

    formatted += f"📊 Всего найдено: {len(results)} товаров"
    return formatted