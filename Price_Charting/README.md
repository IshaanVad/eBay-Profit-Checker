# 📊 PriceCharting - eBay Auction Viewer

A powerful Python GUI tool that lets you compare eBay auction prices to PriceCharting market values for collectible trading cards like Pokémon, Yu-Gi-Oh!, and more.

---

## 🚀 Features

- 🔎 Search eBay with a keyword, search URL, or direct item link
- 📈 Compare total eBay cost (bid + shipping) to market value from PriceCharting
- 💵 See potential **profit** (PriceCharting – eBay total)
- 🌐 Open eBay or PriceCharting links directly from the table
- 🎨 Dark mode GUI for readability
- ⚙️ Multi-threaded price fetching for performance

---

## 🧰 Requirements

### Python packages:

```bash
pip install requests serpapi selenium
```

### WebDriver:

You must have **ChromeDriver** installed and compatible with your version of Google Chrome.

- [Download ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/)

### API Keys:

- ✅ eBay **OAuth Token** (for eBay Browse API)
- ✅ [SerpApi](https://serpapi.com/) **API Key** (for Google Search scraping)

---

## 🔐 Setup

Replace the placeholder strings in the script with your actual tokens:

```python
EBAY_OAUTH_TOKEN = r"""PUT EBAY OAUTH TOKEN HERE"""
SERPAPI_KEY = "PUT SERP API KEY HERE"
```

You can generate:
- eBay OAuth tokens from the [eBay Developer Program](https://developer.ebay.com/)
- SerpApi key from [SerpApi dashboard](https://serpapi.com/dashboard)

---

## 🖥 How to Run

```bash
python pricecharting_ebay_viewer.py
```

---

## 📋 How to Use

1. Type a **keyword**, paste an **eBay item URL**, or use an **eBay search URL**
2. Choose "Auction" or "Buy Now"
3. Click **Search**
4. Review the table:
   - eBay Bid
   - Shipping cost
   - Total cost
   - Time left in auction
   - eBay link (clickable)
   - PriceCharting price (clickable)
   - Profit (green = good deal, red = overpriced)

---

## 📦 Example Output

| Title                 | Bid   | Shipping | Total | Time Left | eBay URL      | PriceCharting | Profit |
|-----------------------|-------|----------|--------|------------|----------------|----------------|--------|
| Charizard PSA 9       | $210  | $5.00    | $215  | 1d 3h      | [link]         | $310.00        | $95.00 |
| Pikachu VMAX BGS 10   | $50   | $10.00   | $60   | 5h 22m     | [link]         | $55.00         | -$5.00 |

---

## 🧠 Behind the Scenes

- eBay data pulled via official **Browse API**
- PriceCharting links found via **SerpApi** + Google Search
- Prices scraped from PriceCharting using **Selenium (headless Chrome)**
- Auction time is auto-formatted from UTC end date

---

## ⚠️ Known Limitations

- Some PriceCharting links may not return valid prices (e.g., for niche cards)
- Rate limits apply for eBay and SerpApi
- Only works with cards that show up in PriceCharting's search results

---

## 🧪 Debugging Tips

- Ensure your **ChromeDriver** is installed and on PATH
- Make sure your tokens are valid and not expired
- Use `print()` debug logs in the script to troubleshoot API or scrape failures

---

## 📄 License

MIT — free to use, modify, and share.

---

## 👨‍💻 Author

Built with ❤️ using Python, SerpApi, and Selenium for collectors and flippers.

