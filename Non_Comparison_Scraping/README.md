# 🛒 eBay Auction Cost Viewer

A simple GUI tool for viewing eBay auction listings with total cost calculation (bid + shipping), built using `tkinter` and the official eBay Browse API.

This tool supports:
- Plain text keywords
- eBay search URLs
- Individual eBay item URLs

Useful for collectors, resellers, or anyone wanting quick insight into the total auction cost of an item.

---

## ✨ Features

- 🔍 Accepts keywords or full eBay search/item URLs
- 🧠 Parses eBay URLs to extract search or item data
- 📦 Displays bid, shipping, and total cost per item
- ⏱ Sorts items by time left (ending soonest first)
- 🔗 Displays direct links to each eBay listing
- 🪟 Clean and simple `tkinter` GUI with scrollable results

---

## 🧰 Requirements

Install Python dependencies:

```bash
pip install requests
```

You also need:
- A valid **OAuth token** for the eBay Browse API

---

## 🔐 Setup

1. Replace the placeholder OAuth token in the script:

```python
token = r"""PASTE_YOUR_EBAY_OAUTH_TOKEN_HERE"""
```

> Note: You can generate a user token using the eBay Developer Program at https://developer.ebay.com/

---

## 🚀 How to Run

```bash
python ebay_auction_viewer.py
```

1. Enter a **search keyword**, **eBay search URL**, or **item URL** (e.g., `https://www.ebay.com/itm/123456789012`)
2. Click **Search**
3. View item listings with:
   - Title
   - Bid price
   - Shipping cost
   - Total cost
   - Time left
   - Clickable item link

---

## 🔎 Supported Inputs

| Input Type         | Example                                                           |
|--------------------|-------------------------------------------------------------------|
| Keyword            | `Charizard PSA 10`                                                |
| eBay Search URL    | `https://www.ebay.com/sch/i.html?_nkw=charizard+psa&_sop=1`       |
| eBay Item URL      | `https://www.ebay.com/itm/123456789012`                           |

---

## 📦 Output Format (Per Item)

```
Charizard Holo 1st Edition PSA 9
 → Bid: $320.00 + Shipping: $5.00 = Total: $325.00
    ⏱ 1d 4h 30m left
    🔗 https://www.ebay.com/itm/123456789012
```

---

## ⚠️ Notes

- Only returns up to 20 items by default
- eBay API rate limits apply
- If shipping/import cost cannot be calculated, it defaults to 0

---

## 📄 License

This project is free to use and modify for personal or educational use.
