import os
import requests
import json
from datetime import datetime

# URL configuration for corpus ingestion
URLS = {
    "nippon_india_large_cap": "https://groww.in/mutual-funds/nippon-india-large-cap-fund-direct-growth",
    "nippon_india_flexi_cap": "https://groww.in/mutual-funds/nippon-india-flexi-cap-fund-direct-growth",
    "nippon_india_growth_mid_cap": "https://groww.in/mutual-funds/nippon-india-growth-mid-cap-fund-direct-growth",
    "nippon_india_small_cap": "https://groww.in/mutual-funds/nippon-india-small-cap-fund-direct-growth",
    "nippon_india_silver_etf_fof": "https://groww.in/mutual-funds/nippon-india-silver-etf-fof-direct-growth",
    "nippon_india_statements": "https://nipponindiaim.com/"
}

# Directory to save raw fetched contents
RAW_DIR = os.path.join("data", "raw")
METADATA_FILE = os.path.join(RAW_DIR, "fetch_metadata.json")

def fetch_all():
    os.makedirs(RAW_DIR, exist_ok=True)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    
    metadata = {}
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, "r") as f:
                metadata = json.load(f)
        except Exception:
            metadata = {}
            
    print(f"Starting fetch at {datetime.now().isoformat()}")
    
    for key, url in URLS.items():
        print(f"Fetching {key} from {url}...")
        timestamp = datetime.now().isoformat()
        try:
            # Short timeout to avoid blocking indefinitely
            response = requests.get(url, headers=headers, timeout=15)
            
            # If we get a 403, Groww/Nippon is blocking the automated request
            if response.status_code == 403:
                print(f"Warning: Access Forbidden (403) for {url}. This might be due to Cloudflare protection.")
                # We will write a fallback template HTML/content so subsequent parsing doesn't fail
                save_fallback_data(key, url, timestamp)
                metadata[key] = {
                    "url": url,
                    "status": f"Fallback (403 Blocked)",
                    "timestamp": timestamp,
                    "file_path": os.path.join(RAW_DIR, f"{key}.html")
                }
                continue
                
            response.raise_for_status()
            
            # Save raw HTML content
            file_name = f"{key}.html"
            file_path = os.path.join(RAW_DIR, file_name)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
                
            print(f"Successfully saved {file_path}")
            metadata[key] = {
                "url": url,
                "status": "Success",
                "timestamp": timestamp,
                "file_path": file_path
            }
            
        except Exception as e:
            print(f"Failed to fetch {key}: {e}")
            save_fallback_data(key, url, timestamp)
            metadata[key] = {
                "url": url,
                "status": f"Fallback (Error: {str(e)})",
                "timestamp": timestamp,
                "file_path": os.path.join(RAW_DIR, f"{key}.html")
            }
            
    # Write metadata JSON
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print("Fetch metadata updated.")

def save_fallback_data(key, url, timestamp):
    """
    Saves fallback mock HTML data derived from the verified local files in corpus
    to ensure the ingestion pipeline works robustly even without internet or when blocked.
    """
    corpus_file_map = {
        "nippon_india_large_cap": "nippon_india_large_cap.txt",
        "nippon_india_flexi_cap": "nippon_india_flexi_cap.txt",
        "nippon_india_growth_mid_cap": "nippon_india_growth_mid_cap.txt",
        "nippon_india_small_cap": "nippon_india_small_cap.txt",
        "nippon_india_silver_etf_fof": "nippon_india_silver_etf_fof.txt",
        "nippon_india_statements": "nippon_india_statements.txt"
    }
    
    corpus_name = corpus_file_map.get(key)
    if not corpus_name:
        return
        
    corpus_path = os.path.join("corpus", corpus_name)
    content = ""
    if os.path.exists(corpus_path):
        with open(corpus_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = f"Scheme Name: {key.replace('_', ' ').title()}\nSource URL: {url}\nLast Updated: {timestamp}\nNo data available."
        
    # Format as mock HTML that can be parsed
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{key.replace('_', ' ').title()}</title>
        <meta name="source_url" content="{url}">
        <meta name="fetch_timestamp" content="{timestamp}">
    </head>
    <body>
        <div id="main-content">
            <pre id="scheme-details">{content}</pre>
        </div>
    </body>
    </html>
    """
    
    file_path = os.path.join(RAW_DIR, f"{key}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Saved fallback mock HTML to {file_path}")

if __name__ == "__main__":
    fetch_all()
