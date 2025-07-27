import requests
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone
import re

# === API Functions ===

def search_auctions(query_dict, token, limit=20):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    params = {
        "q": query_dict["q"],
        "limit": limit
    }

    if query_dict["filter"]:
        params["filter"] = ",".join(query_dict["filter"])
    if query_dict["sort"]:
        params["sort"] = query_dict["sort"]
    if query_dict["category_ids"]:
        params["category_ids"] = query_dict["category_ids"]

    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json().get("itemSummaries", [])

def get_item_by_id(item_id, token):
    url = f"https://api.ebay.com/buy/browse/v1/item/{item_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

# === Helper Functions ===

def get_price(obj):
    try:
        return float(obj.get("value", 0.0))
    except:
        return 0.0

def format_time_left(end_time_str):
    try:
        end_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = end_time - now
        if diff.total_seconds() <= 0:
            return "Auction ended"
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes = remainder // 60
        return f"{days}d {hours}h {minutes}m left"
    except:
        return "Time unknown"

def extract_input_type(text):
    """Returns: ('keyword', query_dict) or ('item_id', value) or ('invalid', None)"""
    text = text.strip()
    if text.startswith("http"):
        parsed = urlparse(text)

        # Handle item URLs
        if "/itm/" in parsed.path:
            match = re.search(r"/itm/(\d+)", parsed.path)
            if match:
                return "item_id", match.group(1)

        # Handle search URLs
        qs = parse_qs(parsed.query)
        keyword = qs.get("nkw", [""])[0] or qs.get("_nkw", [""])[0]

        if not keyword:
            return "invalid", None

        query = {
            "q": keyword,
            "filter": [],
            "sort": None,
            "category_ids": None
        }

        if qs.get("LH_Auction", ["0"])[0] == "1":
            query["filter"].append("buyingOptions:{AUCTION}")

        if "_dcat" in qs:
            query["category_ids"] = qs["_dcat"][0]

        if "_sop" in qs:
            sort_code = qs["_sop"][0]
            sop_map = {
                "1": "endingSoonest",
                "10": "pricePlusShippingLowest",
                "15": "pricePlusShippingHighest",
                "12": "newlyListed"
            }
            query["sort"] = sop_map.get(sort_code)

        return "keyword", query

    # Treat plain input as keyword
    return "keyword", {
        "q": text,
        "filter": ["buyingOptions:{AUCTION}"],
        "sort": None,
        "category_ids": None
    }

def sort_items_by_time_left(items):
    def time_left_seconds(item):
        end = item.get("itemEndDate", "")
        try:
            end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            diff = (end_dt - now).total_seconds()
            return max(diff, 0)
        except:
            return float('inf')
    return sorted(items, key=time_left_seconds)

# === GUI Actions ===

def search_and_display():
    raw_input = entry.get().strip()
    if not raw_input:
        messagebox.showwarning("Input Required", "Please enter a keyword or eBay URL.")
        return

    # === PASTE YOUR OAUTH TOKEN BELOW ===
    token = r"""PUT EBAY OAUTH TOKEN HERE"""

    mode, value = extract_input_type(raw_input)

    if mode == "invalid":
        messagebox.showerror("Invalid URL", "Could not extract a valid search keyword from the URL.")
        return

    try:
        output.delete(1.0, tk.END)

        if mode == "item_id":
            item = get_item_by_id(value, token)
            display_item(item)
        elif mode == "keyword":
            items = search_auctions(value, token)
            if not items:
                output.insert(tk.END, "No auction results found.")
            else:
                items = sort_items_by_time_left(items)
                for item in items:
                    display_item(item)

    except requests.exceptions.HTTPError as e:
        messagebox.showerror("HTTP Error", f"{e.response.status_code}:\n{e.response.text}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def display_item(item):
    title = item.get("title", "Unknown Item")
    bid = get_price(item.get("currentBidPrice", item.get("price", {})))

    # Shipping calculation
    shipping = 0.0
    shipping_opts = item.get("shippingOptions", [])
    costs = []
    for opt in shipping_opts:
        ship_cost = get_price(opt.get("shippingCost", {}))
        import_cost = get_price(opt.get("importCharge", {}))
        total_cost = ship_cost + import_cost
        if total_cost >= 0:
            costs.append(total_cost)
    if costs:
        shipping = min(costs)

    total = bid + shipping
    end_time = item.get("itemEndDate", "")
    time_left = format_time_left(end_time)
    item_url = item.get("itemWebUrl", "#")

    output.insert(
        tk.END,
        f"{title}\n"
        f" → Bid: ${bid:.2f} + Shipping: ${shipping:.2f} = Total: ${total:.2f}\n"
        f"    ⏱ {time_left}\n"
        f"    🔗 {item_url}\n\n"
    )

# === GUI Setup ===

root = tk.Tk()
root.title("eBay Auction Cost Viewer")
root.geometry("750x550")

frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(frame, text="Enter keyword, eBay search URL, or item URL:").pack(anchor=tk.W)
entry = ttk.Entry(frame, width=65)
entry.pack(anchor=tk.W, pady=5)

search_btn = ttk.Button(frame, text="Search", command=search_and_display)
search_btn.pack(anchor=tk.W, pady=5)

output = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=25)
output.pack(fill=tk.BOTH, expand=True, pady=10)

root.mainloop()
