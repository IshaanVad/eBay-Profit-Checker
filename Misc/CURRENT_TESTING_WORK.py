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
import sys

# --- API Keys and Tokens ---
# IMPORTANT: Replace this with your actual, fresh eBay OAuth token.
# eBay OAuth tokens have a limited lifespan and will expire.
# You need to generate a new one from your eBay Developer Account.
EBAY_OAUTH_TOKEN = r"""PUT EBAY OAUTH TOKEN HERE"""

# Your SerpAPI Key
SERPAPI_KEY = "PUT SERP API KEY HERE"

# --- Helper Functions ---

def extract_input_type(text):
    """
    Determines if the input is an eBay URL or a keyword.
    """
    if "ebay.com" in text:
        try:
            query = re.search(r"/itm/(\d+)", text)
            if query:
                return "url", query.group(1)
        except Exception as e:
            print(f"Error extracting item ID from eBay URL: {e}", file=sys.stderr)
            return "invalid", None
    else:
        return "keyword", text

def search_auctions(keyword, token, buying_option="AUCTION"):
    """
    Searches eBay for items based on a keyword and buying option.
    """
    buying_option = buying_option.upper()
    filter_str = ""
    if buying_option == "AUCTION":
        filter_str = "buyingOptions:{AUCTION}"
    elif buying_option == "BUY NOW":
        filter_str = "buyingOptions:{FIXED_PRICE}"

    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={quote_plus(keyword)}"
    if filter_str:
        url += f"&filter={filter_str}"
    url += "&limit=10"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print(f"Making eBay API request to: {url}")
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        print(f"eBay API response status: {r.status_code}")
        return r.json().get("itemSummaries", [])
    except requests.exceptions.RequestException as e:
        print(f"eBay API request failed: {e}", file=sys.stderr)
        messagebox.showerror("API Error", f"Failed to connect to eBay API or request failed: {e}\n\n"
                                          f"If it's a 401 error, your eBay token might be expired or invalid.")
        return []

def get_price(obj):
    """
    Safely extracts price value from a dictionary.
    """
    if obj and "value" in obj:
        try:
            return float(obj["value"])
        except (ValueError, TypeError):
            return 0.0
    return 0.0

def format_time_left(end_time):
    """
    Formats eBay end time into human-readable format.
    """
    try:
        end = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        now = datetime.utcnow()
        delta = end - now
        days = delta.days
        hours, rem = divmod(delta.seconds, 3600)
        minutes, _ = divmod(rem, 60)
        return f"{days}d {hours}h {minutes}m"
    except Exception:
        return "-"

def extract_grade_from_title(title):
    """
    Extracts grading information (e.g., PSA 10, CGC 9.5) from an item title.
    Defaults to "Ungraded" if no specific grade is found.
    """
    grade_match = re.search(r'(PSA|CGC|BGS)\s*(\d+(\.\d+)?)', title, re.IGNORECASE)
    if grade_match:
        return f"{grade_match.group(1).upper()} {grade_match.group(2)}"
    elif re.search(r'ungraded|raw|loose', title, re.IGNORECASE):
        return "Ungraded"
    return "Ungraded"

def get_pricecharting_url(title):
    """
    Uses SerpAPI to find a relevant PriceCharting.com URL for the given title.
    """
    params = {
        "engine": "google",
        "q": f"{title} pricecharting.com pokemon",
        "api_key": SERPAPI_KEY
    }
    print(f"Searching SerpAPI for PriceCharting URL with query: '{params['q']}'")
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        if "error" in results:
            print(f"SerpAPI Error: {results['error']}", file=sys.stderr)
            return None

        for result in results.get("organic_results", []):
            link = result.get("link", "")
            if "pricecharting.com/game/pokemon" in link:
                print(f"Found PriceCharting URL: {link}")
                return link
        print("No relevant PriceCharting URL found in SerpAPI results.")
    except Exception as e:
        print(f"[DEBUG] SerpAPI error for PriceCharting URL: {e}", file=sys.stderr)
    return None

def scrape_pricecharting_price_from_url(url, grade_to_find):
    """
    Scrapes the price for a specific grade from a PriceCharting.com URL using Selenium.
    Includes a fallback to "Ungraded" price if the specific grade is not found.
    Returns the price string and the actual grade key found on PriceCharting.
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    driver = None
    price_str = None
    pc_grade_key_found = "N/A"

    print(f"Attempting to scrape PriceCharting URL: {url} for grade: '{grade_to_find}'")

    try:
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table#graded_table, div.main-content, div.graded-prices"))
        )
        print("PriceCharting page elements seem to be loaded.")

        # Mapping of desired grades to how they appear on PriceCharting for robust matching
        grade_text_map = {
            "ungraded": "Ungraded",
            "psa 10": "PSA 10", "psa 9.5": "PSA 9.5", "psa 9": "PSA 9", "psa 8": "PSA 8", "psa 7": "PSA 7",
            "cgc 10": "CGC 10", "cgc 9.5": "CGC 9.5", "cgc 9": "CGC 9", "cgc 8": "CGC 8",
            "bgs 10": "BGS 10", "bgs 9.5": "BGS 9.5", "bgs 9": "BGS 9", "bgs 8": "BGS 8",
        }
        
        # Normalize the grade to find to PriceCharting's expected format
        pc_grade_to_search = next((v for k, v in grade_text_map.items() if grade_to_find.lower() == k), None)
        
        # If the extracted grade from title was not directly mapped, and it's not explicitly 'ungraded',
        # or if the grade itself suggests ungraded, default to "Ungraded".
        if pc_grade_to_search is None or "ungraded" in grade_to_find.lower():
            pc_grade_to_search = "Ungraded"

        print(f"Normalized PriceCharting grade to search for: '{pc_grade_to_search}'")

        # Attempt to find the price for the specific grade first
        # XPath: finds a td element with normalized text equal to pc_grade_to_search,
        # then finds its following sibling td that contains a '$' sign.
        xpath_specific_grade = f"//td[normalize-space(text())='{pc_grade_to_search}']/following-sibling::td[contains(text(), '$')]"
        print(f"Attempting XPath for specific grade '{pc_grade_to_search}': {xpath_specific_grade}")

        try:
            price_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath_specific_grade))
            )
            price_str = price_element.text.strip()
            pc_grade_key_found = pc_grade_to_search
            print(f"Successfully found price for '{pc_grade_key_found}': {price_str}")
        except Exception as e:
            print(f"Price for '{pc_grade_to_search}' not found directly: {e}. Trying Ungraded as fallback.")
            # Fallback to Ungraded if the specific grade isn't found or timed out
            xpath_ungraded_fallback = "//td[normalize-space(text())='Ungraded']/following-sibling::td[contains(text(), '$')]"
            try:
                price_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath_ungraded_fallback))
                )
                price_str = price_element.text.strip()
                pc_grade_key_found = "Ungraded" # Mark as Ungraded fallback
                print(f"Found Ungraded fallback price: {price_str}")
            except Exception as e:
                print(f"Ungraded fallback price not found either: {e}", file=sys.stderr)
                price_str = None # Ensure price is None if nothing found

    except Exception as e:
        print(f"[DEBUG] Selenium error during scraping PriceCharting URL {url}: {e}", file=sys.stderr)
    finally:
        if driver:
            driver.quit()
            print("Chrome driver quit.")
    return price_str, pc_grade_key_found

def get_pricecharting_data(title):
    """
    Combines URL lookup and scraping for PriceCharting data.
    Returns price_str, URL, and the actual grade found on PriceCharting.
    """
    print(f"Initiating PriceCharting data fetch for title: '{title}'")
    url = get_pricecharting_url(title)
    if not url:
        return (None, None, None) # price_str, url, grade_found
    
    extracted_grade = extract_grade_from_title(title)
    price_str, pc_grade_found = scrape_pricecharting_price_from_url(url, extracted_grade)
    return (price_str, url, pc_grade_found)

# --- Main Application Logic ---

def search_and_display():
    """
    Handles the main search logic, fetches data, and updates the GUI.
    """
    print("\n--- Search button clicked. Starting search_and_display ---")
    raw_input = entry.get().strip()
    if not raw_input:
        messagebox.showwarning("Input Required", "Please enter a keyword or eBay URL.")
        print("Input field is empty.")
        return

    mode, value = extract_input_type(raw_input)
    if mode == "invalid":
        messagebox.showerror("Invalid", "Invalid eBay URL or keyword.")
        print(f"Invalid input type: '{raw_input}'")
        return

    buying_option = buying_option_var.get()
    print(f"Search parameters: Input='{value}', Type='{mode}', Buying Option='{buying_option}'")

    try:
        tree.delete(*tree.get_children())
        print("Treeview cleared.")

        if mode == "keyword":
            print("Fetching items from eBay API...")
            items = search_auctions(value, EBAY_OAUTH_TOKEN, buying_option)
            
            if not items:
                messagebox.showinfo("No Results", "No items found on eBay for your search criteria.")
                print("No items found on eBay for the given keyword.")
                return

            title_to_item = {item.get("title", "Unknown"): item for item in items}
            
            price_charting_data_cache = {}
            print(f"Starting concurrent PriceCharting data fetching for {len(title_to_item)} items...")
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                pc_futures = {executor.submit(get_pricecharting_data, title): title for title in title_to_item}
                
                for future in as_completed(pc_futures):
                    title = pc_futures[future]
                    try:
                        pc_data = future.result()
                        price_charting_data_cache[title] = pc_data
                        print(f"Completed PriceCharting for '{title}'. Data: {pc_data}")
                    except Exception as e:
                        print(f"Error fetching PriceCharting for '{title}': {e}", file=sys.stderr)
                        price_charting_data_cache[title] = (None, None, None)

            print("Processing and displaying results in GUI...")
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
                ebay_url = item.get("itemWebUrl", "")
                
                # Retrieve PriceCharting data
                pc_price_str, pc_link, pc_grade_found = price_charting_data_cache.get(title, (None, None, None))
                
                profit = None
                try:
                    # Validate and convert PriceCharting price string to float for calculation
                    # Check if pc_price_str is not None, not empty, and looks like a number (after cleaning)
                    if pc_price_str and re.match(r'^\$?\d{1,3}(,\d{3})*(\.\d+)?$', pc_price_str.strip()):
                        pc_price = float(pc_price_str.replace("$", "").replace(",", "").strip())
                        if pc_price is not None:
                            profit = round(pc_price - total, 2)
                    else:
                        print(f"Warning: PriceCharting price string '{pc_price_str}' for '{title}' is not a valid number format. Profit not calculated.")

                except (ValueError, TypeError) as e:
                    print(f"Error converting PriceCharting price '{pc_price_str}' to float for '{title}': {e}", file=sys.stderr)
                    profit = None

                profit_display = f"${profit:.2f}" if isinstance(profit, float) else "-"

                tag = ""
                if profit is None:
                    tag = ""
                elif profit > 0:
                    tag = "profit_positive"
                elif profit < 0:
                    tag = "profit_negative"
                
                tree.insert("", tk.END, values=(
                    title,
                    f"${bid:.2f}",
                    f"${shipping:.2f}",
                    f"${total:.2f}",
                    time_left,
                    ebay_url,
                    pc_price_str or "-", # Display only the price
                    pc_link or "-",
                    profit_display
                ), tags=(tag,))
            print("Results displayed in GUI successfully.")
    except Exception as e:
        print(f"An unexpected error occurred in search_and_display: {e}", file=sys.stderr)
        messagebox.showerror("Application Error", f"An unexpected error occurred: {e}\n\n"
                                                  f"Please check your console for detailed error messages.")

def open_link(event):
    """
    Opens eBay or PriceCharting links when a cell is double-clicked.
    """
    selected_item = tree.focus()
    if selected_item:
        region = tree.identify_column(event.x)
        values = tree.item(selected_item, 'values')
        
        # Column indices (0-based):
        # 0: Title, 1: Bid, 2: Shipping, 3: Total, 4: Time Left, 5: eBay URL
        # 6: PriceCharting Price, 7: PriceCharting Link, 8: Profit
        
        # Check for eBay URL column (logical column #6, actual index 5)
        if region == '#6' and len(values) > 5 and values[5].startswith("http"):
            webbrowser.open_new_tab(values[5])
        # Check for PriceCharting Link column (logical column #8, actual index 7)
        elif region == '#8' and len(values) > 7 and values[7].startswith("http"):
            webbrowser.open_new_tab(values[7])

# --- GUI Setup ---

root = tk.Tk()
root.title("PriceCharting vs eBay Auction Viewer")

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

entry = tk.Entry(frame, width=60, bg="#222222", fg=FG_COLOR, insertbackground=FG_COLOR, relief="flat",
                 font=('Arial', 10))
entry.grid(row=0, column=0, padx=5, pady=5)

buying_option_var = tk.StringVar(value="Auction")
buying_option_combo = ttk.Combobox(frame, textvariable=buying_option_var, values=["Auction", "Buy Now"], 
                                   state="readonly", width=10, font=('Arial', 10))
buying_option_combo.grid(row=0, column=1, padx=5, pady=5)
style = ttk.Style()
style.map('TCombobox', fieldbackground=[('readonly', '#222222')], selectbackground=[('readonly', '#333333')],
          selectforeground=[('readonly', FG_COLOR)], background=[('readonly', '#333333')], foreground=[('readonly', FG_COLOR)])


search_button = tk.Button(frame, text="Search", command=search_and_display, 
                          bg="#333333", fg=FG_COLOR, relief="flat", activebackground="#444444",
                          font=('Arial', 10, 'bold'), padx=10, pady=5)
search_button.grid(row=0, column=2, padx=5, pady=5)

# Treeview for displaying results - Updated column name
columns = ("Title", "Bid", "Shipping", "Total", "Time Left", "eBay URL", "PriceCharting Price", "PriceCharting Link", "Profit")
tree = ttk.Treeview(root, columns=columns, show="headings", selectmode="browse")
tree.pack(padx=10, pady=10, fill="both", expand=True)

# Configure Treeview style
style.theme_use('default')

style.configure("Treeview",
                background=TREE_BG,
                foreground=TREE_FG,
                fieldbackground=TREE_BG,
                rowheight=25,
                borderwidth=0,
                relief="flat",
                font=('Arial', 10))

style.map('Treeview',
           background=[('selected', '#555555')],
           foreground=[('selected', 'white')])

style.configure("Treeview.Heading",
                background="#333333",
                foreground=FG_COLOR,
                font=('Arial', 10, 'bold'),
                relief="flat")

tree.tag_configure('oddrow', background=TREE_ALT_BG)
tree.tag_configure('evenrow', background=TREE_BG)

tree.tag_configure("profit_positive", foreground=PROFIT_GREEN)
tree.tag_configure("profit_negative", foreground=PROFIT_RED)

for col_name in columns:
    tree.heading(col_name, text=col_name)
    tree.column(col_name, width=120, anchor="w")
    
tree.column("Title", width=250)
tree.column("eBay URL", width=240)
tree.column("PriceCharting Price", width=150, anchor="center") # Adjusted width and centered
tree.column("PriceCharting Link", width=240)
tree.column("Profit", width=80, anchor="center")

tree.bind("<Double-1>", open_link)

root.mainloop()