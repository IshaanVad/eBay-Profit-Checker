# TCG Price Comparator (eBay vs TCG Player or Price Charting)

This is a GUI-based Python tool for comparing **TCG (Trading Card Game)** listings on **eBay** (like Pokémon, Yu-Gi-Oh, Magic: The Gathering) against **PriceCharting** market values. It helps users identify potentially undervalued cards on eBay based on current auction or buy-now listings.

---

## 🔍 Features

- Search by **keyword** (e.g., "Charizard PSA 8") or **direct eBay URL**
- View eBay **bid**, **shipping**, and **total cost**
- View estimated market value from **PriceCharting.com**
- Automatically calculates **potential profit**
- Filter by **Auction** or **Buy Now**
- Clickable links to both **eBay** and **PriceCharting** entries
- Built-in **dark mode** with colored profit indicators (green = profit, red = loss)
- Multithreaded to perform price comparisons in parallel for faster results

---

## 🛠️ Installation

1. **Clone this repository**:

   ```bash
   git clone https://github.com/yourusername/tcg-price-comparator.git
   cd tcg-price-comparator
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   Make sure you have the following installed:
   - Python 3.8+
   - Google Chrome and compatible [Chromedriver](https://chromedriver.chromium.org/)
   - [Selenium](https://pypi.org/project/selenium/)
   - [SerpAPI](https://serpapi.com/) account and API key

3. **Create or update your `.env` file or hardcode** in the script:

   - Your **eBay OAuth token** (for official eBay API access)
   - Your **SerpAPI key**

---

## 🚀 Running the App

```bash
python tcg_price_viewer.py
```

Replace `tcg_price_viewer.py` with the actual filename of the script if different.

---

## 📦 How It Works

1. **eBay Listings**:
   - Uses the official eBay Browse API to get current auctions or fixed-price listings.

2. **Market Price Lookup**:
   - Parses the card title to extract key identifiers (e.g., `"Charizard PSA 9"`).
   - Uses **SerpAPI** to Google search for the matching **PriceCharting** product page.
   - Scrapes the market price using **headless Selenium**.

3. **Profit Calculation**:
   - Compares the total eBay cost (bid + shipping) with the PriceCharting market value.
   - Displays the difference as a **profit/loss column**.

---

## 🧠 Intelligent Title Parsing

To ensure better PriceCharting accuracy, the tool:
- Extracts up to the first 3 capitalized keywords from the eBay title
- Prioritizes recognized grades like **PSA**, **BGS**, **CGC**, etc.
- Ignores noise words like "Near Mint", "Holo", "Foil", etc. in searches

---

## 🖱️ UI Interaction

- **Double-click** on:
  - The **eBay URL** column to open the listing
  - The **PriceCharting Link** column to view the price data page

---

## 🛡️ Notes

- **This tool is intended for TCG cards** (e.g., Pokémon, Yu-Gi-Oh, MTG). Accuracy for sports or other collectibles may be reduced.
- Scraping PriceCharting is done responsibly and with rate-limiting via Selenium and threading.
- You should comply with eBay and PriceCharting's terms of service when using this tool.

---

## 📸 Screenshot

![screenshot](screenshot.png)  
_(Add your own screenshot showing the tool in use)_

---

## 📃 License

MIT License

---

## 📫 Contact

For questions, suggestions, or contributions:  
**Your Name** — [@yourhandle](https://github.com/yourhandle)

---

## 🧩 TODO / Enhancements

- [ ] Add export to CSV or Excel
- [ ] Add support for sports cards or other collectibles
- [ ] Add more granular filters (grade, set, language, etc.)
- [ ] Display card image thumbnails from eBay

