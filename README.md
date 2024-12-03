# ShodanEyes 🔍

A lightweight tool inspired by Censys's host exploration feature called [Censeye](https://github.com/Censys-Research/censeye) and described [here](https://censys.com/automated-hunting/), but designed for Shodan. This tool helps you find similar hosts based on specific attributes of a target IP address.

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
- Supports multiple IP analysis mode
- Identifies unique characteristics across all services/ports
- Highlights interesting results (hosts with ≤200 matches)

## Usage 💻

Single IP mode: 
- python main.py 1.2.3.4

Multiple IPs mode:
- python main.py 1.2.3.4 5.6.7.8 9.10.11.12


The tool will:
1. Fetch all available data for the IP from Shodan
2. In multiple IP mode:
   - Identify shared parameters between IPs
   - Focus analysis on common attributes
   - Optimize API queries by analyzing only relevant shared characteristics
3. Extract unique values for each field
4. Search Shodan for other hosts with matching attributes
5. Display results, highlighting particularly unique characteristics

## Output Example 📋

<img width="340" alt="Screenshot 2024-11-28 152909" src="https://github.com/user-attachments/assets/e77ecedf-86d7-4ccc-b8c4-97288ea9dbf3">

## Differences from Censeye 🔄

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

## Disclaimer

This is an independent project that uses the publicly available Shodan API. "Shodan" is a trademark of Shodan HQ LLC. This tool is not officially supported by Shodan.

## Notes 📌
> [!CAUTION]
> Rate limiting is NOT implemented to prevent API exhaustion


> [!CAUTION]
> API queries count against your Shodan API limits


