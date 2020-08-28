
import logging

from bs4 import BeautifulSoup
import requests
from requests.exceptions import InvalidSchema
from requests.exceptions import ConnectionError

logging.basicConfig(
    level=logging.ERROR,
    format='[%(name)s] [%(levelname)s] [%(asctime)s] - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_html(url: str) -> str:
    """Get html code from a URL.
    Args:
        url: URL to visit.
    Return:
        HTML code.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
    except InvalidSchema:
        return
    except ConnectionError:
        logger.error("Connection error [%s]" % url)
        return
    else:
        if response.status_code != 200:
            logger.info("Error loading page [%s]" % url)
            return
        return response.text


def parse_item(item):
    result = {}
    brand = item['data-webm-make']
    model = item['data-webm-model']
    net_id = item['data-webm-networkid']
    price = item['data-webm-price']
    state = item['data-webm-state']
    seller_type = item.find('span', class_='seller-type').contents[-1]
    year = item.find("a", {
        "data-webm-clickvalue": "sv-title"}).contents[-1].split(' ')[0]

    result = {
        'brand': item['data-webm-make'],
        'model': item['data-webm-model'],
        'net_id': item['data-webm-networkid'],
        'price': item['data-webm-price'],
        'state': item['data-webm-state'],
        'seller_type': item.find('span', class_='seller-type').contents[-1],
        'year': year,
    }

    for key_detail in item.find_all("div", class_="key-detail-value"):
        key_detail_type = key_detail['data-type'].lower().replace(" ", "_")
        # logger.debug(f"{key_detail_type}: {key_detail.contents[-1]}")
        result[key_detail_type] = key_detail.contents[-1]
    return result


def scraper(url: str, pagination_limit=5) -> None:
    base_url = "https://www.chileautos.cl"
    result = []
    for i in range(pagination_limit):
        logger.info(f"Scraping [{url}]")
        soup = BeautifulSoup(get_html(url), 'html.parser')
        items = soup.find_all('div', class_='listing-item standard')
        for item in items:
            logger.debug(parse_item(item))
            result.append(parse_item(item))
        next_btn = soup.find('a', class_='page-link next')
        if next_btn and 'href' in next_btn.attrs:
            url = base_url + next_btn.attrs['href']
            logger.info(f"Pagination - URL = [{url}]")
            continue
        next_btn = soup.find_all('a', class_='page-link next disabled')
        if next_btn:
            logger.info("Last page!")
            break
        else:
            logger.error("PAGINATION ERROR")
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Scraping chileautos.cl')
    parser.add_argument('--page', help='URL for the start page', required=True)
    parser.add_argument(
        '--pagination_limit',
        help='Maximum number of pages visited',
        required=True)
    args = parser.parse_args()

    scraper(url=args.page, pagination_limit=10)
