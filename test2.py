# test2.py
import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductParser:
    """Класс для парсинга товаров из различных магазинов"""

    @staticmethod
    def search_all_markets(query: str, max_results: int = 5) -> str:
        """Поиск товаров в нескольких маркетплейсах"""
        results = []

        try:
            # Поиск в DNS
            dns_result = ProductParser.dns_search_uc(query, max_results)
            if "Результаты поиска" in dns_result or "📱" in dns_result:
                results.append(dns_result)

            # Поиск в Ситилинк
            citilink_result = ProductParser.citilink_search(query, max_results)
            if "Результаты поиска" in citilink_result or "💻" in citilink_result:
                results.append(citilink_result)

            # Поиск в Яндекс.Маркет
            market_result = ProductParser.yandex_market_search(query, max_results)
            if market_result:
                results.append(market_result)

            if results:
                return "\n\n" + "═" * 40 + "\n\n".join(results)
            else:
                return f"❌ Не удалось найти товары по запросу '{query}' ни в одном магазине.\nПопробуйте другой запрос, например:\n- /parser ноутбук\n- /parser наушники\n- /parser телефон"

        except Exception as e:
            logger.error(f"Ошибка в search_all_markets: {e}")
            return f"❌ Произошла ошибка при поиске: {str(e)}"

    @staticmethod
    def dns_search_uc(query: str, max_results: int = 5) -> str:
        """Поиск товаров в DNS"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            }

            # Формируем URL для поиска в DNS
            search_url = f"https://www.dns-shop.ru/search/?q={quote_plus(query)}&stock=now"
            logger.info(f"Запрос к DNS: {search_url}")

            response = requests.get(search_url, headers=headers, timeout=15)

            if response.status_code != 200:
                return f"❌ DNS вернул код {response.status_code}"

            soup = BeautifulSoup(response.content, 'html.parser')

            result_text = f"🛒 **DNS - результаты по запросу '{query}':**\n\n"

            # Способ 1: Поиск по новому классу (актуальный)
            product_cards = soup.find_all('div', class_=lambda x: x and 'product-card' in x.lower())

            # Способ 2: Альтернативный поиск
            if not product_cards:
                product_cards = soup.find_all('div', {'data-id': 'product'})

            # Способ 3: Поиск по структуре
            if not product_cards:
                product_cards = soup.find_all('a', class_='catalog-product__name')
                if product_cards:
                    # Если нашли ссылки, берем их родительские элементы
                    product_cards = [card.parent for card in product_cards[:max_results]]

            found_count = 0
            for card in product_cards[:max_results]:
                try:
                    # Название товара
                    name_elem = card.find(['a', 'span'], class_=lambda x: x and any(
                        word in str(x).lower() for word in ['name', 'title', 'product-name']
                    ))

                    if not name_elem:
                        name_elem = card.find(['a', 'span'], string=True)

                    name = name_elem.text.strip()[:100] if name_elem else "Без названия"

                    # Цена
                    price_elem = card.find(['span', 'div'], class_=lambda x: x and any(
                        word in str(x).lower() for word in ['price', 'cost', 'value']
                    ))

                    if not price_elem:
                        price_elem = card.find(['span', 'div'], string=lambda x: x and '₽' in str(x))

                    price = price_elem.text.strip() if price_elem else "Цена не указана"

                    # Ссылка
                    link_elem = card.find('a', href=True)
                    if link_elem:
                        href = link_elem['href']
                        link = f"https://www.dns-shop.ru{href}" if href.startswith('/') else href
                    else:
                        link = search_url

                    # Рейтинг
                    rating_elem = card.find(['div', 'span'], class_=lambda x: x and any(
                        word in str(x).lower() for word in ['rating', 'star', 'review']
                    ))
                    rating = rating_elem.text.strip() if rating_elem else "—"

                    result_text += f"📱 **{name}**\n"
                    result_text += f"💰 Цена: {price}\n"
                    if rating != "—":
                        result_text += f"⭐ Рейтинг: {rating}\n"
                    result_text += f"🔗 [Открыть товар]({link})\n"
                    result_text += "─" * 30 + "\n"

                    found_count += 1

                except Exception as e:
                    logger.warning(f"Ошибка при обработке карточки: {e}")
                    continue

            if found_count > 0:
                return result_text + f"\n✅ Найдено товаров: {found_count}"
            else:
                return f"❌ В DNS по запросу '{query}' ничего не найдено\n\n💡 Попробуйте:\n1. Упростить запрос\n2. Проверить наличие товара в наличии\n3. Использовать английские названия"

        except requests.exceptions.Timeout:
            return "⏰ Таймаут при обращении к DNS"
        except requests.exceptions.ConnectionError:
            return "🔌 Ошибка подключения к DNS"
        except Exception as e:
            logger.error(f"Критическая ошибка DNS: {e}")
            return f"❌ Ошибка при поиске в DNS"

    @staticmethod
    def citilink_search(query: str, max_results: int = 5) -> str:
        """Поиск товаров в Ситилинк"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }

            url = f"https://www.citilink.ru/search/?text={quote_plus(query)}"
            logger.info(f"Запрос к Ситилинк: {url}")

            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code != 200:
                return f"❌ Ситилинк вернул код {response.status_code}"

            soup = BeautifulSoup(response.content, 'html.parser')

            result_text = f"🏪 **Ситилинк - результаты по запросу '{query}':**\n\n"

            # Ищем товары разными способами
            products = []

            # Способ 1: По data-атрибутам
            products = soup.find_all('div', {'data-meta-name': True})
            products = [p for p in products if 'Product' in p.get('data-meta-name', '')]

            # Способ 2: По классам
            if not products:
                products = soup.find_all('div', class_=lambda x: x and 'product_data' in str(x).lower())

            # Способ 3: По структуре товаров
            if not products:
                # Ищем все div с информацией о товарах
                all_divs = soup.find_all('div')
                products = [div for div in all_divs if any(
                    word in div.get('class', []) for word in ['product', 'item', 'card']
                ) if isinstance(div.get('class'), list)]

            found_count = 0
            for product in products[:max_results]:
                try:
                    # Название
                    name_elem = product.find(['a', 'span', 'div'], class_=lambda x: x and any(
                        word in str(x).lower() for word in ['name', 'title', 'product-name']
                    ))

                    if not name_elem:
                        # Ищем текст с названием
                        name_elem = product.find(['a', 'span', 'div'], string=True)
                        if name_elem and len(name_elem.text.strip()) > 10:
                            name = name_elem.text.strip()[:80]
                        else:
                            continue
                    else:
                        name = name_elem.text.strip()[:80]

                    # Цена
                    price_elem = product.find(['span', 'div'], class_=lambda x: x and any(
                        word in str(x).lower() for word in ['price', 'cost', 'current']
                    ))

                    if not price_elem:
                        price_elem = product.find(['span', 'div'], string=lambda x: x and '₽' in str(x))

                    price = price_elem.text.strip()[:50] if price_elem else "Цена не указана"

                    # Ссылка
                    link_elem = product.find('a', href=True)
                    if link_elem:
                        href = link_elem['href']
                        link = f"https://www.citilink.ru{href}" if href.startswith('/') else href
                    else:
                        link = url

                    result_text += f"💻 **{name}**\n"
                    result_text += f"💰 Цена: {price}\n"
                    result_text += f"🔗 [Открыть товар]({link})\n"
                    result_text += "─" * 30 + "\n"

                    found_count += 1

                except Exception as e:
                    logger.warning(f"Ошибка обработки товара Ситилинк: {e}")
                    continue

            if found_count > 0:
                return result_text + f"\n✅ Найдено товаров: {found_count}"
            else:
                # Альтернативный ответ
                return f"🏪 **Ситилинк**\n🔍 По запросу '{query}' найдены товары\n📱 [Открыть поиск в Ситилинк]({url})\n\n💡 Нажмите на ссылку для просмотра результатов"

        except requests.exceptions.Timeout:
            return "⏰ Таймаут при обращении к Ситилинк"
        except requests.exceptions.ConnectionError:
            return "🔌 Ошибка подключения к Ситилинк"
        except Exception as e:
            logger.error(f"Ошибка парсинга Ситилинк: {e}")
            return f"🏪 **Ситилинк**\n🔍 [Открыть поиск по запросу '{query}'](https://www.citilink.ru/search/?text={quote_plus(query)})"

    @staticmethod
    def yandex_market_search(query: str, max_results: int = 3) -> str:
        """Поиск в Яндекс.Маркет"""
        try:
            url = f"https://market.yandex.ru/search?text={quote_plus(query)}&how=aprice"
            return f"🛒 **Яндекс.Маркет**\n🔍 По запросу '{query}' найдены товары\n📱 [Открыть поиск с сортировкой по цене]({url})\n\n💡 Яндекс.Маркет покажет актуальные цены и наличие в разных магазинах"
        except:
            return ""

    @staticmethod
    def dns_search(query: str, max_results: int = 5) -> str:
        """Альтернативный метод поиска в DNS (для совместимости)"""
        return ProductParser.dns_search_uc(query, max_results)


# Функции для обратной совместимости
def search_all_markets(query: str, max_results: int = 5) -> str:
    """Главная функция поиска (публичный интерфейс)"""
    return ProductParser.search_all_markets(query, max_results)


def dns_search_uc(query: str, max_results: int = 5) -> str:
    """Функция для совместимости с вашим ботом"""
    return ProductParser.dns_search_uc(query, max_results)


def dns_search(query: str, max_results: int = 5) -> str:
    """Альтернативная функция DNS поиска"""
    return ProductParser.dns_search(query, max_results)


def citilink_search(query: str, max_results: int = 5) -> str:
    """Функция поиска в Ситилинк"""
    return ProductParser.citilink_search(query, max_results)


def yandex_market_search(query: str, max_results: int = 3) -> str:
    """Функция поиска в Яндекс.Маркет"""
    return ProductParser.yandex_market_search(query, max_results)


# Пример использования и тестирование
if __name__ == "__main__":
    print("🔍 Тестирование парсера товаров...")
    print("=" * 60)

    # Тестовые запросы
    test_queries = ["ноутбук", "наушники", "телефон", "монитор"]

    for query in test_queries[:1]:  # Тестируем только первый запрос
        print(f"\n📋 Тестируем запрос: '{query}'")
        print("-" * 40)

        # Тест DNS
        print("\n1. Тест DNS:")
        result_dns = dns_search_uc(query, max_results=3)
        print(result_dns[:500] + "..." if len(result_dns) > 500 else result_dns)

        # Тест Ситилинк
        print("\n2. Тест Ситилинк:")
        result_citilink = citilink_search(query, max_results=3)
        print(result_citilink[:500] + "..." if len(result_citilink) > 500 else result_citilink)

        # Тест общего поиска
        print("\n3. Тест общего поиска:")
        result_all = search_all_markets(query, max_results=2)
        print(result_all)

        break  # Остановиться после первого запроса для краткости

    print("\n" + "=" * 60)
    print("✅ Тестирование завершено!")
    print("\n💡 Использование в боте:")
    print("1. Сохраните этот файл как test2.py")
    print("2. В основном файле бота используйте:")
    print('   result = test2.dns_search_uc("ноутбук")')
    print("3. Или для общего поиска:")
    print('   result = test2.search_all_markets("наушники")')