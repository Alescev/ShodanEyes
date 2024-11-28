# Shodan Host Explorer 🔍

A lightweight tool inspired by [Censys](https://censys.io/)'s host exploration feature, but designed for Shodan. This tool helps you find similar hosts based on specific attributes of a target IP address.

(This project is not affiliated with, endorsed by, or connected to Shodan or Censys in any way)

## Features ✨

- Analyzes multiple host attributes including:
  - HTTP headers hash
  - Favicon hash
  - HTML content hash
  - HTTP titles
  - SSL certificate details
  - JARM fingerprints
  - Product information
- Identifies unique characteristics across all services/ports
- Highlights interesting results (hosts with ≤200 matches)
- User-friendly colored output
- Rate-limiting protection

## Usage 💻

Run the script with an IP address: 

"python main.py 1.2.3.4"


The tool will:
1. Fetch all available data for the IP from Shodan
2. Extract unique values for each field
3. Search Shodan for other hosts with matching attributes
4. Display results, highlighting particularly unique characteristics

## Output Example 📋
...


## Differences from Censys 🔄

While inspired by Censys's similar hosts feature, this tool:
- Works with Shodan's data structure
- Focuses on a smaller set of key attributes
- Provides immediate results without complex processing
- Is designed for quick reconnaissance

## Requirements 📝

- Python 3.6+
- Shodan API key
- Required packages:
  - shodan
  - colorama
  - argparse

## Notes 📌

- Rate limiting is NOT implemented to prevent API exhaustion
- Some fields might not be available for all hosts
- API queries count against your Shodan API limits

## Disclaimer

This is an independent project that uses the publicly available Shodan API. "Shodan" is a trademark of Shodan HQ LLC. This tool is maintained by the community and is not officially supported by Shodan.