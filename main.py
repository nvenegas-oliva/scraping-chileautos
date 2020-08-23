
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
logger.setLevel(logging.DEBUG)


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
    brand = item['data-webm-make']
    model = item['data-webm-model']
    net_id = item['data-webm-networkid']
    price = item['data-webm-price']
    state = item['data-webm-state']
    seller_type = item.find('span', class_='seller-type').contents[-1]

    print(f"brand: {brand}")
    print(f"model: {model}")
    print(f"net_id: {net_id}")
    print(f"price: {price}")
    print(f"state: {state}")
    print(f"seller_type: {seller_type}")

    for key_detail in item.find_all("div", class_="key-detail-value"):
        key_detail_type = key_detail['data-type'].lower().replace(" ", "_")
        print(f"{key_detail_type}: {key_detail.contents[-1]}")


if __name__ == '__main__':
    url = 'https://www.chileautos.cl/vehiculos/ssangyong/tivoli/'

    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')

    # listing-item standard
    # listing-item showcase # premium o otros intereses
    items = soup.find_all('div', class_='listing-item standard')

    parse_item(items[0])
