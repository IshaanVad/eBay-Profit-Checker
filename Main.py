import requests
from bs4 import BeautifulSoup

url = 'https://www.ebay.com/sch/i.html?_nkw=pokemon&_sacat=0&_from=R40&LH_Auction=1&rt=nc&LH_PrefLoc=1&Language=English&_dcat=183454'

headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

combined_prices = {}

for item in soup.select('.s-item'):
    title_elem = item.select_one('.s-item__title')
    price_elem = item.select_one('.s-item__price')
    shipping_elem = item.select_one('.s-item__shipping, .s-item__logisticsCost')  # shipping cost

    if not title_elem or not price_elem:
        continue  # Skip incomplete listings

    title = title_elem.get_text(strip=True)

    try:
        # Extract price, remove $ and commas
        price_text = price_elem.get_text()
        price = float(price_text.replace('$', '').replace(',', '').split()[0])
    except:
        continue  # Skip if price can't be parsed

    try:
        shipping_text = shipping_elem.get_text()
        if 'Free' in shipping_text:
            shipping = 0.0
        else:
            shipping = float(shipping_text.replace('$', '').replace('+', '').replace(',', '').split()[0])
    except:
        shipping = 0.0  # Assume free shipping if missing

    total = round(price + shipping, 2)
    combined_prices[title] = total

# Print result
for name, total in combined_prices.items():
    print(f"{name} → ${total}")
