import shodan
from colorama import init, Fore, Style
import time
import argparse
import sys
try:
    from config import SHODAN_API_KEY
except ImportError:
    print(f"{Fore.RED}Error: config.py file not found or SHODAN_API_KEY not defined.")
    print(f"Please create a config.py file with your Shodan API key.{Style.RESET_ALL}")
    sys.exit(1)

# Initialize colorama for cross-platform color support
init()

# Initialize Shodan client
api = shodan.Shodan(SHODAN_API_KEY)

# Fields we want to check from a host's data
fields_to_check = [
    'http.headers_hash',
    'http.favicon.hash',
    'http.html_hash',
    'http.title',
    'ssl.cert.fingerprint',
    'ssl.cert.issuer.cn',
    'ssl.cert.subject.cn',
    'ssl.jarm',
    'product'
]

max_interesting_count = 200  # Updated to 200 as requested

def print_banner():
    """Print a styled banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                     Shodan Host Explorer                     ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(Fore.CYAN + banner + Style.RESET_ALL)

def print_section(title):
    """Print a section header"""
    print(f"\n{Fore.YELLOW}{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}{Style.RESET_ALL}\n")

def get_host_data(ip):
    """Get host information from Shodan"""
    try:
        print(f"{Fore.BLUE}⚡ Fetching data for IP: {Fore.WHITE}{ip}{Style.RESET_ALL}")
        host = api.host(ip)
        print(f"{Fore.GREEN}✔ Host data retrieved successfully{Style.RESET_ALL}")
        return host
    except shodan.APIError as e:
        print(f"{Fore.RED}✘ Error fetching data for IP {ip}: {e}{Style.RESET_ALL}")
        return None

def extract_values_from_host(host_data):
    """Extract searchable values from host data"""
    values = {}
    # Initialize dictionary with empty sets for each field
    for field in fields_to_check:
        values[field] = set()
    
    # Collect all unique values for each field across all services
    for item in host_data.get('data', []):
        for field in fields_to_check:
            keys = field.split('.')
            value = item
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    value = None
                    break
            if value is not None:
                # Convert dictionary values to strings for hashing
                if isinstance(value, dict):
                    value = str(value)
                # Convert lists to tuples for hashing
                elif isinstance(value, list):
                    value = tuple(value)
                try:
                    values[field].add(value)
                except TypeError:
                    print(f"{Fore.YELLOW}Warning: Could not add value for field {field}{Style.RESET_ALL}")
                    continue
    
    # Convert sets to list for easier handling
    return {k: list(v) for k, v in values.items() if v}

def search_similar_hosts(field, value):
    """Search Shodan for hosts with similar values"""
    try:
        query = f'{field}:"{value}"' if isinstance(value, str) else f'{field}:{value}'
        results = api.count(query)
        return results['total']
    except shodan.APIError as e:
        print(f"{Fore.RED}✘ Error searching for {query}: {e}{Style.RESET_ALL}")
        return None

def format_result(query, count):
    """Format a single result with proper styling"""
    if count <= max_interesting_count:
        return f"{Fore.GREEN}▶ {query}{Style.RESET_ALL}\n  └─ {Fore.CYAN}{count:,} hosts{Style.RESET_ALL} {Fore.YELLOW}(Interesting!){Style.RESET_ALL}"
    else:
        return f"{Fore.WHITE}▶ {query}{Style.RESET_ALL}\n  └─ {Fore.CYAN}{count:,} hosts{Style.RESET_ALL}"

def main(ip):
    print_banner()
    
    # Get the host data
    print_section("Host Information")
    host_data = get_host_data(ip)
    if not host_data:
        return

    # Extract values from the host
    print_section("Value Extraction")
    values = extract_values_from_host(host_data)
    if not values:
        print(f"{Fore.RED}No searchable values found in host data.{Style.RESET_ALL}")
        return
    
    total_values = sum(len(vals) for vals in values.values())
    print(f"{Fore.GREEN}✔ Found {total_values} searchable values across {len(values)} fields{Style.RESET_ALL}")

    # Search for similar hosts
    print_section("Similar Hosts Search")
    results = {}
    for field, value_list in values.items():
        for value in value_list:
            print(f"{Fore.BLUE}⚡ Searching for {field}...{Style.RESET_ALL}", end='\r')
            count = search_similar_hosts(field, value)
            if count is not None:
                results[f"{field}:{value}"] = count
            time.sleep(0.1)  # Prevent rate limiting

    # Display results
    print_section("Search Results")
    if not results:
        print(f"{Fore.RED}No results found.{Style.RESET_ALL}")
        return

    # Sort results by count
    sorted_results = sorted(results.items(), key=lambda x: x[1])
    
    # Display interesting results first
    interesting_found = False
    for query, count in sorted_results:
        if count <= max_interesting_count:
            print(format_result(query, count))
            interesting_found = True
    
    if interesting_found:
        print(f"\n{Fore.YELLOW}{'─' * 60}{Style.RESET_ALL}\n")
    
    # Display other results
    for query, count in sorted_results:
        if count > max_interesting_count:
            print(format_result(query, count))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Shodan Host Explorer - Find similar hosts based on specific attributes')
    parser.add_argument('ip', help='IP address to analyze')
    args = parser.parse_args()

    main(args.ip)
