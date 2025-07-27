# 🃏 TCGPlayer - eBay Viewer

A GUI application that helps compare eBay auction listings with TCGPlayer prices to identify potential arbitrage opportunities in **trading card games** such as **Pokémon**, **Yu-Gi-Oh!**, and **Magic: The Gathering**.

## ✨ Features

- 🔍 Search eBay auctions or "Buy Now" listings by keyword or URL.
- 📈 Retrieve up to 10 active eBay listings using the official eBay Browse API.
- 🧠 Use SerpAPI + Google to find corresponding TCGPlayer product pages.
- 💸 Automatically scrape and display TCGPlayer prices using headless Chrome.
- 💰 Calculate potential **profit margin** between eBay total price and TCGPlayer price.
- 🌚 Clean **dark mode** GUI built with `tkinter` and `ttk`.
- 🔗 Clickable eBay and TCGPlayer links directly from the interface.
- ⚡ Multi-threaded TCGPlayer price fetching for speed.

---

## 🧰 Requirements

Install dependencies:

```bash
pip install requests serpapi selenium
```

You also need:

- Google Chrome installed
- ChromeDriver (matching your Chrome version) in your system PATH
- A [SerpAPI](https://serpapi.com/) API key
- A valid eBay OAuth token with access to the Browse API

---

## 🔐 Setup

Edit the top of the script:

```python
EBAY_OAUTH_TOKEN = r"""INSERT EBAY OAUTH TOKEN HERE"""
SERPAPI_KEY = "INSERT SERP API KEY HERE"
```

---

## 🚀 How to Run

```bash
python tcg_ebay_viewer.py
```

Enter a keyword (e.g., `Charizard PSA 9`) or an eBay item URL, choose a buying option, and click **Search**. The app will:

1. Query eBay’s Browse API for up to 10 items.
2. Retrieve shipping + bid/price data.
3. Search Google for the TCGPlayer product page.
4. Scrape and display the current TCGPlayer price.
5. Calculate and display profit margin.

---

## 📊 Output Table Columns

| Column        | Description                                      |
|---------------|--------------------------------------------------|
| Title         | eBay listing title                               |
| Bid           | Current bid or price                             |
| Shipping      | Lowest shipping/import cost                      |
| Total         | Bid + shipping                                   |
| Time Left     | Time left in the auction                         |
| eBay URL      | Clickable link to the eBay listing               |
| TCG Price     | TCGPlayer price scraped from the product page    |
| TCG Link      | Clickable link to the TCGPlayer page             |
| Profit        | TCGPrice − Total (green if positive, red if negative) |

---

## ⚠️ Notes

- If a matching TCGPlayer page is not found, price/profit will be blank.
- If scraping fails (e.g., page structure changes), TCG price may be missing.
- This app uses multithreading, but TCGPlayer page load times may vary.
- This is intended for **TCG cards** like **Pokémon**, **Yu-Gi-Oh!**, and **Magic: The Gathering**.

---

## 🛠 Troubleshooting

- **OAuth Errors**: Ensure your eBay token is fresh and has correct scopes.
- **ChromeDriver Issues**: Make sure your ChromeDriver version matches your Chrome version.
- **SerpAPI Failures**: Ensure you have quota left and the key is valid.
- **Scraping Errors**: Site changes or captchas may break scraping.

---

## 📄 License

This project is free to use and modify for personal or educational purposes.

