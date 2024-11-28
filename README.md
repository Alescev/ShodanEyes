# ShodanEyes 🔍

A lightweight tool inspired by Censys's host exploration feature called [Censeye](https://github.com/Censys-Research/censeye) and described [here](https://censys.com/automated-hunting/), but designed for Shodan. This tool helps you find similar hosts based on specific attributes of a target IP address.

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
> [!CAUTION]
> Rate limiting is NOT implemented to prevent API exhaustion


> [!CAUTION]
> API queries count against your Shodan API limits


