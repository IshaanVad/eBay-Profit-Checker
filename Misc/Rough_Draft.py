import requests
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# === STEP 1: Search Auction Listings ===
def search_auctions(keyword, token, limit=20):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {
        "q": keyword,
        "filter": "buyingOptions:{AUCTION}",
        "limit": limit
    }

    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json().get("itemSummaries", [])

# === STEP 2: Extract & Compute Prices ===
def get_price(obj):
    try:
        return float(obj.get("value", 0.0))
    except:
        return 0.0

def compute_total_cost(items):
    result = {}
    for item in items:
        title = item.get("title", "Unknown Item")
        bid = get_price(item.get("currentBidPrice", {}))
        shipping = 0.0
        shipping_opts = item.get("shippingOptions", [])

        if shipping_opts:
            shipping = min([
                get_price(opt.get("shippingCost", {})) + get_price(opt.get("importCharge", {}))
                for opt in shipping_opts
            ])

        total = bid + shipping
        result[title] = total
    return result

# === STEP 3: GUI Logic ===
def search_and_display():
    keyword = entry.get().strip()
    if not keyword:
        messagebox.showwarning("Input Required", "Please enter a search term.")
        return

    # ==== PASTE YOUR OAUTH TOKEN HERE (IN QUOTES) ====
    token = "PASTE HERE"

    try:
        items = search_auctions(keyword, token)
        results = compute_total_cost(items)

        output.delete(1.0, tk.END)
        if not results:
            output.insert(tk.END, "No auction results found.")
        else:
            for title, cost in results.items():
                output.insert(tk.END, f"{title}\n → ${cost:.2f}\n\n")
    except requests.exceptions.HTTPError as e:
        messagebox.showerror("Search Error", f"HTTP Error {e.response.status_code}:\n{e.response.text}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# === STEP 4: Build GUI ===
root = tk.Tk()
root.title("eBay Auction Total Cost Viewer")
root.geometry("700x500")

frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(frame, text="Enter eBay Search Term:").pack(anchor=tk.W)
entry = ttk.Entry(frame, width=50)
entry.pack(anchor=tk.W, pady=5)

search_btn = ttk.Button(frame, text="Search Auctions", command=search_and_display)
search_btn.pack(anchor=tk.W, pady=5)

output = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=20)
output.pack(fill=tk.BOTH, expand=True, pady=10)

root.mainloop()
