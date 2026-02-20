"""
Export pitch deck to PDF with all slides properly formatted
Requires: playwright
Install: pip install playwright
Then run: playwright install chromium
"""

import asyncio
import os
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("ERROR: playwright not installed")
    print("Please run: pip install playwright")
    print("Then run: playwright install chromium")
    exit(1)

async def export_to_pdf():
    """Export the pitch deck HTML to PDF with all slides"""
    
    # Get paths
    script_dir = Path(__file__).parent
    html_file = script_dir / "index.html"
    pdf_file = script_dir / "Pitch_Deck_Soccer_Analytics.pdf"
    
    if not html_file.exists():
        print(f"ERROR: {html_file} not found")
        return
    
    print("Starting PDF export...")
    print(f"Input: {html_file}")
    print(f"Output: {pdf_file}")
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Load the HTML file
        await page.goto(f"file:///{html_file.absolute().as_posix()}")
        
        # Wait for page to load
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)  # Extra wait for animations
        
        # Export to PDF
        await page.pdf(
            path=str(pdf_file),
            format='A4',
            print_background=True,
            margin={
                'top': '0',
                'right': '0',
                'bottom': '0',
                'left': '0'
            },
            prefer_css_page_size=False
        )
        
        await browser.close()
    
    print(f"\n✓ PDF exported successfully!")
    print(f"Location: {pdf_file}")
    print(f"Size: {pdf_file.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    asyncio.run(export_to_pdf())
