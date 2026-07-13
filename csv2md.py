#!/usr/bin/env python3
"""
CSV to Markdown Converter for Bookstores Directory
Generates a formatted README.md from bookstores.csv

Usage:
    python csv_to_markdown.py [--input BOOKSTORES.CSV] [--output BOOKSTORES.MD]
"""

import csv
import argparse
from collections import defaultdict
from datetime import datetime


def read_csv(filepath):
    """Read CSV file and return list of dictionaries."""
    stores = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stores.append(row)
    return stores


def group_by_municipality(stores):
    """Group stores by municipality."""
    grouped = defaultdict(list)
    for store in stores:
        muni = store.get('Municipality', 'Unknown')
        grouped[muni].append(store)
    return dict(grouped)


def escape_md(value):
    """Escape pipe characters in markdown tables."""
    if value is None or value.strip() == '':
        return '—'
    # Escape pipe characters and handle line breaks
    escaped = str(value).replace('|', '\\|').replace('\n', '<br>')
    return escaped


def generate_summary_table(stores, municipalities):
    """Generate the summary statistics table."""
    total = len(stores)
    
    md_lines = [
        "## Summary Statistics",
        "",
        "| Metric | Value |",
        "|--------|-------|"
    ]
    
    md_lines.append(f"| Total Bookstores | {total} |")
    muni_names = ", ".join(sorted(municipalities.keys()))
    md_lines.append(f"| Municipalities | {len(municipalities)} ({muni_names}) |")
    md_lines.append(f"| Data Last Updated | {datetime.now().strftime('%B %Y')} |")
    
    return "\n".join(md_lines)


def generate_store_table(stores, include_coords=True):
    """Generate a markdown table for a list of stores."""
    
    headers = ["Name", "Latitude", "Longitude", "Municipality", 
               "Address", "Phone", "Website", "Facebook", "Instagram"]
    
    if not include_coords:
        headers = ["Name", "Municipality", "Address", "Phone", 
                   "Website", "Facebook", "Instagram"]
    
    md_lines = []
    md_lines.append("| " + " | ".join(headers) + " |")
    md_lines.append("| " + "--- | " * len(headers))
    
    for store in stores:
        row = []
        for col in headers:
            val = store.get(col, '')
            row.append(escape_md(val))
        md_lines.append("| " + " | ".join(row) + " |")
    
    return "\n".join(md_lines)


def generate_distribution_table(municipalities):
    """Generate the distribution by municipality table."""
    total = sum(len(s) for s in municipalities.values())
    
    md_lines = [
        "## 📊 Distribution by Municipality",
        "",
        "| Municipality | Number of Stores | Percentage |",
        "|--------------|------------------|------------|"
    ]
    
    for muni, stores in sorted(municipalities.items(), key=lambda x: -len(x[1])):
        count = len(stores)
        pct = (count / total * 100) if total > 0 else 0
        md_lines.append(f"| {muni} | {count} | {pct:.0f}% |")
    
    return "\n".join(md_lines)


def generate_quick_links(stores):
    """Generate quick links section for notable entries."""
    md_lines = [
        "## 🔗 Quick Links",
        ""
    ]
    
    # Find store with website
    stores_with_website = [s for s in stores if s.get('Website', '').strip()]
    if stores_with_website:
        for s in stores_with_website:
            name = escape_md(s['Name'])
            url = escape_md(s['Website'])
            md_lines.append(f"- **[🌐 Website]** [{name}]({url})")
    
    # Find store with phone
    stores_with_phone = [s for s in stores if s.get('Phone', '').strip()]
    if stores_with_phone:
        phones = ", ".join([f"{s['Name']} ({escape_md(s['Phone'])})" for s in stores_with_phone])
        md_lines.append(f"- **📞 Phone Listed:** {phones}")
    
    return "\n".join(md_lines)


def main():
    parser = argparse.ArgumentParser(
        description='Convert bookstores.csv to markdown format'
    )
    parser.add_argument('--input', '-i', default='bookstores.csv',
                        help='Input CSV file path (default: bookstores.csv)')
    parser.add_argument('--output', '-o', default='bookstores.md',
                        help='Output MD file path (default: bookstores.md)')
    parser.add_argument('--no-coords', action='store_true',
                        help='Exclude latitude/longitude columns')
    
    args = parser.parse_args()
    
    try:
        # Read CSV
        print(f"Reading {args.input}...")
        stores = read_csv(args.input)
        
        # Group by municipality
        municipalities = group_by_municipality(stores)
        
        # Generate markdown content
        md_content = [
            "# Bookstores Directory",
            "",
            "A curated collection of independent bookstores in the Lisbon metropolitan area.",
            "",
        ]
        
        # Add sections
        md_content.append(generate_summary_table(stores, municipalities))
        md_content.append("")
        md_content.append("---")
        md_content.append("")
        md_content.append("## 📚 Bookstore Listings")
        md_content.append("")
        
        # Add stores by municipality
        for muni, muni_stores in sorted(municipalities.items()):
            md_content.append(f"### {muni} ({len(muni_stores)} stores)")
            md_content.append("")
            md_content.append(generate_store_table(muni_stores, not args.no_coords))
            md_content.append("")
            md_content.append("---")
            md_content.append("")
        
        # Add additional sections
        md_content.append(generate_distribution_table(municipalities))
        md_content.append("")
        md_content.append("---")
        md_content.append("")
        md_content.append(generate_quick_links(stores))
        md_content.append("")
        md_content.append("---")
        md_content.append("")
        md_content.append(f"*Generated from `{args.input}` on {datetime.now().strftime('%Y-%m-%d')} — All data as recorded in source file.*")
        
        # Write output
        full_content = "\n".join(md_content)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"✅ Successfully generated {args.output}")
        print(f"   - Processed {len(stores)} bookstores")
        print(f"   - Found {len(municipalities)} municipalities")
        
    except FileNotFoundError:
        print(f"❌ Error: Input file '{args.input}' not found.")
        print("   Make sure the CSV file exists in the current directory.")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    main()