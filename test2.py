import time
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import sys


def dns_search_uc(query: str, limit: int = 5, timeout: int = 50):
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1366,768")
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")

    # Для Render.com добавляем эти опции
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-features=VizDisplayCompositor")

    results = []

    try:
        print(f"Начинаю поиск: {query}")

        # Явно указываем путь к Chrome для Render.com
        chrome_options = {
            'version_main': 143,  # Версия Chrome, которую вы скачали в логах
        }

        # Используем undetected_chromedriver с явными настройками
        driver = uc.Chrome(
            options=options,
            driver_executable_path='/usr/local/bin/chromedriver',
            browser_executable_path='/usr/bin/google-chrome-stable'
        )

        print("Chrome запущен успешно")

        try:
            driver.get(f"https://www.dns-shop.ru/search/?q={query}")
            print(f"Открыта страница поиска: {query}")

            # Ждем загрузки товаров
            WebDriverWait(driver, timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".catalog-product, .product"))
            )
            time.sleep(2.0)

            html = driver.page_source
            print(f"Страница загружена, HTML получен ({len(html)} символов)")

            soup = BeautifulSoup(html, "lxml")

            # Ищем карточки товаров
            cards = soup.select(".catalog-product, .product")
            print(f"Найдено карточек товаров: {len(cards)}")

            for i, card in enumerate(cards[:limit], 1):
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

                print(f"Добавлен товар {i}: {title[:50]}...")

                if len(results) >= limit:
                    break

            print(f"Поиск завершен. Найдено товаров: {len(results)}")

        except Exception as e:
            print(f"Ошибка при поиске на странице: {e}")
            import traceback
            print(traceback.format_exc())
            results.append({"error": f"Ошибка при парсинге: {str(e)}"})

        finally:
            driver.quit()
            print("Chrome закрыт")

        return results

    except Exception as e:
        print(f"Общая ошибка: {e}")
        import traceback
        print(traceback.format_exc())
        return [{"error": f"Ошибка при запуске Chrome: {str(e)}"}]


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