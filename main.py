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
    """Format a single result with proper styling and make it clickable"""
    base_url = "https://www.shodan.io/search?query="
    query_url = f"{base_url}{query.replace(':', '%3A').replace(' ', '+')}"
    
    if count <= max_interesting_count:
        # Create a clickable link using ANSI escape sequences
        clickable_link = f"\033]8;;{query_url}\033\\{query_url}\033]8;;\033\\"
        return f"{Fore.GREEN}▶ {query}{Style.RESET_ALL} ({clickable_link})\n  └─ {Fore.CYAN}{count:,} hosts{Style.RESET_ALL} {Fore.YELLOW}(Interesting!){Style.RESET_ALL}"
    else:
        return f"{Fore.WHITE}▶ {query}{Style.RESET_ALL}\n  └─ {Fore.CYAN}{count:,} hosts{Style.RESET_ALL}"

def main(ips):
    print_banner()
    
    # Split the input IPs and strip any whitespace
    ip_list = [ip.strip() for ip in ips.split(',')]
    
    # If single IP, mention we're in single-host mode
    if len(ip_list) == 1:
        print(f"{Fore.BLUE}Running in single-host mode{Style.RESET_ALL}")
    else:
        print(f"{Fore.BLUE}Running in multi-host mode with {len(ip_list)} hosts{Style.RESET_ALL}")
    
    # Get the host data for each IP
    all_values = []
    for ip in ip_list:
        print_section(f"Host Information for {ip}")
        host_data = get_host_data(ip)
        if not host_data:
            return
        values = extract_values_from_host(host_data)
        if not values:
            print(f"{Fore.RED}No searchable values found in host data for {ip}.{Style.RESET_ALL}")
            return
        all_values.append(values)
    
    # For single IP, use all values. For multiple IPs, find common values
    if len(ip_list) == 1:
        search_values = all_values[0]
    else:
        search_values = {}
        for field in fields_to_check:
            sets = [set(values.get(field, [])) for values in all_values]
            common_set = set.intersection(*sets)
            if common_set:
                search_values[field] = list(common_set)
        
        if not search_values:
            print(f"{Fore.RED}No common searchable values found across provided IPs.{Style.RESET_ALL}")
            return
    
    total_values = sum(len(vals) for vals in search_values.values())
    if len(ip_list) == 1:
        print(f"{Fore.GREEN}✔ Found {total_values} searchable values across {len(search_values)} fields{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}✔ Found {total_values} common searchable values across {len(search_values)} fields{Style.RESET_ALL}")

    # Search for similar hosts
    print_section("Similar Hosts Search")
    results = {}
    for field, value_list in search_values.items():
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
    parser.add_argument('ips', nargs='+', help='IP addresses to analyze, separated by spaces')
    args = parser.parse_args()

    # Join the IPs with commas to match the expected input format
    main(','.join(args.ips))
