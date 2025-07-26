import requests
from bs4 import BeautifulSoup

def get_ebay_item_total(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'https://www.ebay.com/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    with requests.Session() as session:
        response = session.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page, status code {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        title_tag = soup.find(id="itemTitle")
        if not title_tag:
            print("Could not find item title.")
            return None
        title = title_tag.get_text(strip=True).replace("Details about  \xa0", "")

        bid_price_tag = soup.find('span', id='prcIsum_bidPrice') or soup.find('span', id='prcIsum')
        if not bid_price_tag:
            print("Could not find current bid or price.")
            return None

        bid_price_text = bid_price_tag.get_text(strip=True)
        bid_price = float(bid_price_text.replace('$', '').replace(',', ''))

        shipping_tag = soup.find('span', id='fshippingCost')
        if not shipping_tag:
            shipping_price = 0.0
        else:
            shipping_text = shipping_tag.get_text(strip=True)
            if 'Free' in shipping_text:
                shipping_price = 0.0
            else:
                shipping_price = float(shipping_text.replace('$', '').replace(',', ''))

        total_price = bid_price + shipping_price

        return {title: total_price}

if __name__ == "__main__":
    url = input("Enter eBay item URL: ").strip()
    result = get_ebay_item_total(url)
    if result:
        print("Resulting map:")
        print(result)
