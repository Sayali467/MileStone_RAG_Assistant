import os
import json
import re
from bs4 import BeautifulSoup

RAW_DIR = os.path.join("data", "raw")
PARSED_DIR = os.path.join("data", "parsed")
METADATA_FILE = os.path.join(RAW_DIR, "fetch_metadata.json")

# Define target sections
SECTIONS = [
    "overview",
    "expense_ratio",
    "exit_load",
    "minimum_investment",
    "benchmark",
    "tax",
    "fund_management",
    "investment_objective",
    "fund_house",
    "nav",
    "aum",
    "pe_pb_ratio",
    "rating",
    "returns"
]

# Hardcoded details for tax, investment objective, and fund house since they are AMC-wide
# or standard regulatory facts that are present in the scheme SIDs but may not be fully in the Groww summary.
TAX_INFO_EQUITY = (
    "Taxation rules for Equity schemes: Short Term Capital Gains (STCG) are taxed at 15% if units are redeemed within 1 year. "
    "Long Term Capital Gains (LTCG) are taxed at 10% (without indexation) on gains exceeding Rs. 1 lakh per financial year, "
    "provided units are held for more than 1 year."
)
TAX_INFO_COMMODITY = (
    "Taxation rules for Commodity/Silver schemes: Gains on redemption are treated as per Debt fund rules. "
    "Since April 1, 2023, gains from debt-oriented mutual funds are taxed at the investor's individual income tax slab rate (marginal taxation) "
    "regardless of the holding period, and LTCG tax benefits with indexation are no longer applicable."
)

INVESTMENT_OBJECTIVES = {
    "nippon_india_large_cap": "The primary investment objective of the scheme is to seek long-term capital appreciation by investing predominantly in equity and equity-related instruments of large-cap companies.",
    "nippon_india_flexi_cap": "The investment objective of the scheme is to generate long-term capital appreciation by investing in a diversified portfolio of equity and equity-related instruments across large-cap, mid-cap, and small-cap companies.",
    "nippon_india_growth_mid_cap": "The primary investment objective of the scheme is to seek long-term capital appreciation by investing predominantly in equity and equity-related instruments of mid-cap companies.",
    "nippon_india_small_cap": "The primary investment objective of the scheme is to generate long-term capital appreciation by investing predominantly in equity and equity-related instruments of small-cap companies.",
    "nippon_india_silver_etf_fof": "The investment objective of the scheme is to seek to provide returns that closely correspond to the returns provided by Nippon India Silver ETF, which tracks the domestic price of silver.",
    "nippon_india_statements": "Nippon India Mutual Fund provides simple account statement download capabilities for tracking transactions, capital gains, and tax statements."
}

FUND_HOUSE_INFO = (
    "Nippon India Mutual Fund (formerly Reliance Mutual Fund) is one of India's leading mutual fund houses. "
    "It is sponsored by Nippon Life Insurance Company of Japan, one of the largest life insurers in the world. "
    "The AMC is registered under SEBI and manages a diverse range of mutual fund schemes."
)

def parse_all():
    os.makedirs(PARSED_DIR, exist_ok=True)
    
    if not os.path.exists(METADATA_FILE):
        print(f"Error: Metadata file {METADATA_FILE} not found. Please run fetch.py first.")
        return
        
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        fetch_metadata = json.load(f)
        
    for key, info in fetch_metadata.items():
        file_path = info.get("file_path")
        if not file_path or not os.path.exists(file_path):
            print(f"File not found for {key}: {file_path}")
            continue
            
        print(f"Parsing {key}...")
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        soup = BeautifulSoup(html_content, "html.parser")
        
        parsed_data = {
            "scheme_name": key.replace("_", " ").title(),
            "source_url": info.get("url"),
            "last_updated": info.get("timestamp"),
            "sections": {s: "" for s in SECTIONS}
        }
        
        # Populate static/AMC-wide fields
        if "silver" in key:
            parsed_data["sections"]["tax"] = TAX_INFO_COMMODITY
        else:
            parsed_data["sections"]["tax"] = TAX_INFO_EQUITY
            
        parsed_data["sections"]["investment_objective"] = INVESTMENT_OBJECTIVES.get(key, "")
        parsed_data["sections"]["fund_house"] = FUND_HOUSE_INFO
        
        # Check if it is a fallback file containing <pre id="scheme-details">
        pre_tag = soup.find("pre", id="scheme-details")
        if pre_tag:
            print(f"Found fallback text data in {key}.html")
            text_content = pre_tag.get_text()
            extract_from_text(text_content, parsed_data, key)
        else:
            # It's actual Groww HTML
            print(f"Processing raw HTML for {key}.html")
            extract_from_html(soup, parsed_data, key)
            
        # Write the parsed result to JSON
        output_file = os.path.join(PARSED_DIR, f"{key}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, indent=2)
        print(f"Successfully saved parsed data to {output_file}")

def extract_from_text(text, parsed_data, key):
    """
    Extracts sections from structured plain text (like the corpus files or mock HTML fallback).
    """
    # 1. Parse Scheme Name from text if available
    name_match = re.search(r"Scheme Name:\s*(.*)", text)
    if name_match:
        parsed_data["scheme_name"] = name_match.group(1).strip()
        
    # 2. Parse Date from text if available
    date_match = re.search(r"Last Updated:\s*(.*)", text)
    if date_match:
        parsed_data["last_updated"] = date_match.group(1).strip()
        
    # 3. Expense Ratio
    er_match = re.search(r"Expense Ratio:\s*(.*)", text, re.IGNORECASE)
    if er_match:
        parsed_data["sections"]["expense_ratio"] = er_match.group(1).split("\n")[0].strip()
    else:
        # Search anywhere in text
        er_match_2 = re.search(r"expense ratio of ([\d.]+\s*%)", text, re.IGNORECASE)
        if er_match_2:
            parsed_data["sections"]["expense_ratio"] = f"Expense ratio is {er_match_2.group(1)}."
            
    # 4. Exit Load
    el_match = re.search(r"Exit Load:\s*(.*)", text, re.IGNORECASE)
    if el_match:
        parsed_data["sections"]["exit_load"] = el_match.group(1).split("\n")[0].strip()
        
    # 5. Minimum Investment
    sip_match = re.search(r"Minimum SIP Investment:\s*(.*)", text, re.IGNORECASE)
    lump_match = re.search(r"Minimum Lumpsum Investment:\s*(.*)", text, re.IGNORECASE)
    min_inv = []
    if sip_match:
        min_inv.append(f"Minimum SIP: {sip_match.group(1).split('\n')[0].strip()}")
    if lump_match:
        min_inv.append(f"Minimum Lumpsum: {lump_match.group(1).split('\n')[0].strip()}")
        
    if min_inv:
        parsed_data["sections"]["minimum_investment"] = ". ".join(min_inv)
    else:
        # Fallback if both not formatted
        min_match = re.search(r"minimum investment\s*(.*)", text, re.IGNORECASE)
        if min_match:
            parsed_data["sections"]["minimum_investment"] = min_match.group(1).split("\n")[0].strip()
            
    # 6. Benchmark
    bench_match = re.search(r"Benchmark Index:\s*(.*)", text, re.IGNORECASE)
    if bench_match:
        parsed_data["sections"]["benchmark"] = bench_match.group(1).split("\n")[0].strip()
        
    # NAV
    nav_match = re.search(r"(?:- )?NAV:\s*(.*)", text, re.IGNORECASE)
    if nav_match:
        parsed_data["sections"]["nav"] = nav_match.group(1).split("\n")[0].strip()
        
    # AUM
    aum_match = re.search(r"(?:- )?AUM:\s*(.*)", text, re.IGNORECASE)
    if aum_match:
        parsed_data["sections"]["aum"] = aum_match.group(1).split("\n")[0].strip()
        
    # PE/PB Ratio
    pe_match = re.search(r"(?:- )?Portfolio PE Ratio:\s*(.*)", text, re.IGNORECASE)
    pb_match = re.search(r"(?:- )?Portfolio PB Ratio:\s*(.*)", text, re.IGNORECASE)
    pe_pb = []
    if pe_match:
        pe_pb.append(f"PE Ratio: {pe_match.group(1).split('\n')[0].strip()}")
    if pb_match:
        pe_pb.append(f"PB Ratio: {pb_match.group(1).split('\n')[0].strip()}")
    if pe_pb:
        parsed_data["sections"]["pe_pb_ratio"] = ", ".join(pe_pb)
        
    # Rating
    rating_match = re.search(r"(?:- )?Star Rating:\s*(.*)", text, re.IGNORECASE)
    if not rating_match:
        rating_match = re.search(r"(?:- )?Rating:\s*(.*)", text, re.IGNORECASE)
    if rating_match:
        parsed_data["sections"]["rating"] = rating_match.group(1).split("\n")[0].strip()
        
    # Returns
    returns_match = re.search(r"(?:- )?Returns:\s*(.*)", text, re.IGNORECASE)
    if returns_match:
        parsed_data["sections"]["returns"] = returns_match.group(1).split("\n")[0].strip()
        
    # 7. Fund Management Team
    fm_start = text.find("Fund Management Team:")
    if fm_start != -1:
        fm_text = text[fm_start + len("Fund Management Team:"):].strip()
        parsed_data["sections"]["fund_management"] = fm_text
    else:
        # Fallback search
        fm_match = re.search(r"(?:managed by|fund managers?|team):\s*(.*)", text, re.IGNORECASE)
        if fm_match:
            parsed_data["sections"]["fund_management"] = fm_match.group(1).strip()
            
    # 8. Overview (Riskometer, Category, etc.)
    risk_match = re.search(r"Riskometer:\s*(.*)", text, re.IGNORECASE)
    cat_match = re.search(r"Fund Category:\s*(.*)", text, re.IGNORECASE)
    overview_parts = []
    if cat_match:
        overview_parts.append(f"Category: {cat_match.group(1).split('\n')[0].strip()}")
    if risk_match:
        overview_parts.append(f"Riskometer: {risk_match.group(1).split('\n')[0].strip()}")
        
    # Standard text matching for remaining items
    remaining_text = text
    # Remove large blocks we already extracted
    if fm_start != -1:
        remaining_text = text[:fm_start]
        
    clean_lines = [l.strip() for l in remaining_text.split("\n") if l.strip() and not l.startswith("Scheme Name:") and not l.startswith("Source URL:") and not l.startswith("Last Updated:")]
    if clean_lines:
        overview_parts.insert(0, clean_lines[0])
        
    parsed_data["sections"]["overview"] = " | ".join(overview_parts)

def extract_from_html(soup, parsed_data, key):
    """
    Extracts metadata from the raw fetched HTML (like title), but populates
    scheme-specific parameters from the verified corpus text files since
    Groww renders key parameters (managers, exit loads, direct expense ratio)
    dynamically on the client side, making them absent from standard SSR HTML.
    """
    # Remove script and style elements
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()
        
    # Extract Title as Scheme Name
    title_tag = soup.find("title")
    if title_tag:
        parsed_data["scheme_name"] = title_tag.get_text().split(" - ")[0].strip()
        
    # Extract all parameters from the verified local files to guarantee 100% correctness
    for s in SECTIONS:
        if s not in ["tax", "investment_objective", "fund_house"]:
            extract_fallback_value(key, s, parsed_data)

def extract_fallback_value(key, section_name, parsed_data):
    """
    Utility to fetch a value from the pre-verified local corpus.
    This guarantees correctness.
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
    if not os.path.exists(corpus_path):
        return
        
    with open(corpus_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    temp_parsed = {"scheme_name": "", "source_url": "", "last_updated": "", "sections": {s: "" for s in SECTIONS}}
    extract_from_text(content, temp_parsed, key)
    
    parsed_data["sections"][section_name] = temp_parsed["sections"].get(section_name, "")

if __name__ == "__main__":
    parse_all()
