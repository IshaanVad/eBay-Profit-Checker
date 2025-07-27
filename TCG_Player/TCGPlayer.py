import tkinter as tk
from tkinter import ttk, messagebox
import requests
from urllib.parse import quote_plus
from serpapi import GoogleSearch
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import webbrowser

EBAY_OAUTH_TOKEN = r"""INSERT EBAY OAUTH TOKEN HERE"""
SERPAPI_KEY = "INSERT SERP API KEY HERE"

def extract_input_type(text):
    if "ebay.com" in text:
        try:
            query = re.search(r"/itm/(\d+)", text)
            if query:
                return "url", query.group(1)
        except:
            return "invalid", None
    else:
        return "keyword", text

def search_auctions(keyword, token, buying_option="AUCTION"):
    buying_option = buying_option.upper()
    if buying_option == "AUCTION":
        filter_str = "buyingOptions:{AUCTION}"
    elif buying_option == "BUY NOW":
        filter_str = "buyingOptions:{FIXED_PRICE}"
    else:
        filter_str = ""

    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={quote_plus(keyword)}"
    if filter_str:
        url += f"&filter={filter_str}"
    url += "&limit=10"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    r = requests.get(url, headers=headers)
    return r.json().get("itemSummaries", [])

def get_price(obj):
    if obj and "value" in obj:
        return float(obj["value"])
    return 0.0

def format_time_left(end_time):
    try:
        end = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        now = datetime.utcnow()
        delta = end - now
        days = delta.days
        hours, rem = divmod(delta.seconds, 3600)
        minutes, _ = divmod(rem, 60)
        return f"{days}d {hours}h {minutes}m"
    except:
        return "-"

def get_tcgplayer_url(title):
    params = {
        "engine": "google",
        "q": f"{title} site:tcgplayer.com",
        "api_key": SERPAPI_KEY
    }
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        for result in results.get("organic_results", []):
            link = result.get("link", "")
            if "tcgplayer.com/product" in link:
                return link
    except Exception as e:
        print("[DEBUG] SerpAPI error:", e)
    return None

def scrape_tcgplayer_price_from_url(url):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span[class*='price']"))
        )
        price_elements = driver.find_elements(By.CSS_SELECTOR, "span[class*='price']")
        for el in price_elements:
            price_text = el.text.strip()
            if "$" in price_text and "Market" not in price_text:
                match = re.search(r"\$\d{1,4}(\.\d{2})?", price_text)
                if match:
                    return match.group(0)
        text = driver.page_source
        match = re.search(r"\$\d{1,4}(\.\d{2})?", text)
        if match:
            return match.group(0)
    except Exception as e:
        print("[DEBUG] TCGPlayer scraping error:", e)
    finally:
        driver.quit()
    return None

def get_tcgplayer_price(title):
    url = get_tcgplayer_url(title)
    if not url:
        return (None, None)
    price = scrape_tcgplayer_price_from_url(url)
    return (price, url)

def search_and_display():
    raw_input = entry.get().strip()
    if not raw_input:
        messagebox.showwarning("Input Required", "Please enter a keyword or eBay URL.")
        return

    mode, value = extract_input_type(raw_input)
    if mode == "invalid":
        messagebox.showerror("Invalid", "Invalid eBay URL or keyword.")
        return

    buying_option = buying_option_var.get()

    try:
        tree.delete(*tree.get_children())
        if mode == "keyword":
            items = search_auctions(value, EBAY_OAUTH_TOKEN, buying_option)
            title_to_item = {item.get("title", "Unknown"): item for item in items}
            tcg_cache = {}
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = {executor.submit(get_tcgplayer_price, title): title for title in title_to_item}
                for future in as_completed(futures):
                    title = futures[future]
                    try:
                        tcg_cache[title] = future.result()
                    except:
                        tcg_cache[title] = (None, None)

            for title, item in title_to_item.items():
                bid = get_price(item.get("currentBidPrice", item.get("price", {})))
                shipping = 0.0
                costs = []
                for opt in item.get("shippingOptions", []):
                    ship = get_price(opt.get("shippingCost", {})) + get_price(opt.get("importCharge", {}))
                    if ship >= 0:
                        costs.append(ship)
                if costs:
                    shipping = min(costs)
                total = bid + shipping
                time_left = format_time_left(item.get("itemEndDate", ""))
                url = item.get("itemWebUrl", "")
                tcg_price_str, tcg_link = tcg_cache.get(title, (None, None))

                try:
                    tcg_price = float(tcg_price_str.replace("$", "")) if tcg_price_str and "$" in tcg_price_str else None
                    profit = round(tcg_price - total, 2) if tcg_price is not None else None
                except:
                    profit = None

                profit_display = f"${profit:.2f}" if isinstance(profit, float) else "-"

                # Decide tag for coloring profit column (red, green, or default)
                if profit is None or profit == 0:
                    tag = ""
                elif profit > 0:
                    tag = "profit_positive"
                else:
                    tag = "profit_negative"

                tree.insert("", tk.END, values=(
                    title,
                    f"${bid:.2f}",
                    f"${shipping:.2f}",
                    f"${total:.2f}",
                    time_left,
                    url,
                    tcg_price_str or "-",
                    tcg_link or "-",
                    profit_display
                ), tags=(tag,))
    except Exception as e:
        messagebox.showerror("Error", str(e))

def open_link(event):
    selected_item = tree.focus()
    if selected_item:
        region = tree.identify_column(event.x)
        values = tree.item(selected_item, 'values')
        if region == '#6' and values[5].startswith("http"):
            webbrowser.open_new_tab(values[5])
        elif region == '#8' and values[7].startswith("http"):
            webbrowser.open_new_tab(values[7])

root = tk.Tk()
root.title("TCGPlayer vs eBay Auction Viewer")

# Dark mode colors
BG_COLOR = "#121212"
FG_COLOR = "white"
TREE_BG = "#1e1e1e"
TREE_ALT_BG = "#2c2c2c"
TREE_FG = "white"
PROFIT_GREEN = "#00ff00"
PROFIT_RED = "#ff5555"

root.configure(bg=BG_COLOR)

frame = tk.Frame(root, bg=BG_COLOR)
frame.pack(padx=10, pady=10)

entry = tk.Entry(frame, width=60, bg="#222222", fg=FG_COLOR, insertbackground=FG_COLOR, relief="flat")
entry.grid(row=0, column=0, padx=5)

buying_option_var = tk.StringVar(value="Auction")
buying_option_combo = ttk.Combobox(frame, textvariable=buying_option_var, values=["Auction", "Buy Now"], state="readonly", width=10)
buying_option_combo.grid(row=0, column=1, padx=5)

search_button = tk.Button(frame, text="Search", command=search_and_display, bg="#333333", fg=FG_COLOR, relief="flat", activebackground="#444444")
search_button.grid(row=0, column=2, padx=5)

columns = ("Title", "Bid", "Shipping", "Total", "Time Left", "eBay URL", "TCG Price", "TCG Link", "Profit")
tree = ttk.Treeview(root, columns=columns, show="headings", selectmode="browse")
tree.pack(padx=10, pady=10, fill="both", expand=True)

style = ttk.Style()
style.theme_use('default')

# Treeview style for dark mode
style.configure("Treeview",
                background=TREE_BG,
                foreground=TREE_FG,
                fieldbackground=TREE_BG,
                highlightthickness=0,
                bd=0,
                font=('Arial', 10))

style.map('Treeview', background=[('selected', '#555555')], foreground=[('selected', 'white')])

style.configure("Treeview.Heading",
                background="#333333",
                foreground=FG_COLOR,
                relief="flat")

# Alternate row colors
tree.tag_configure('oddrow', background=TREE_ALT_BG)
tree.tag_configure('evenrow', background=TREE_BG)

# Tags for profit coloring
tree.tag_configure("profit_positive", foreground=PROFIT_GREEN)
tree.tag_configure("profit_negative", foreground=PROFIT_RED)

# Set column widths & anchors
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120, anchor="w")
tree.column("Title", width=250)
tree.column("eBay URL", width=240)
tree.column("TCG Link", width=240)
tree.column("Profit", width=80, anchor="center")

tree.bind("<Double-1>", open_link)

root.mainloop()
