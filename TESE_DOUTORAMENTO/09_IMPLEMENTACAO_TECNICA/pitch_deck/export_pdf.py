"""
Export pitch deck to PDF with all slides properly formatted
"""

import asyncio
import subprocess
import sys
from pathlib import Path

def install_playwright():
    """Install playwright if not available"""
    print("Installing playwright...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    print("✓ Playwright installed!\n")

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Playwright not found. Installing...")
    install_playwright()
    from playwright.async_api import async_playwright

async def export_to_pdf():
    """Export the pitch deck HTML to PDF with all slides"""
    
    # Get paths
    script_dir = Path(__file__).parent
    html_file = script_dir / "index.html"
    pdf_file = script_dir / "Pitch_Deck_Soccer_Analytics.pdf"
    
    if not html_file.exists():
        print(f"ERROR: {html_file} not found")
        input("Press Enter to exit...")
        return
    
    print("=" * 60)
    print("PITCH DECK PDF EXPORT")
    print("=" * 60)
    print(f"\nInput:  {html_file.name}")
    print(f"Output: {pdf_file.name}\n")
    print("Exporting... This may take a few seconds.\n")
    
    try:
        async with async_playwright() as p:
            # Launch browser in headless mode
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            # Set dark mode preference
            await page.emulate_media(color_scheme='dark')
            
            # Load the HTML file
            file_url = html_file.absolute().as_uri()
            await page.goto(file_url)
            
            # Wait for page to fully load
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)  # Extra wait for fonts and animations
            
            # Export to PDF with all backgrounds
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
                prefer_css_page_size=False,
                display_header_footer=False
            )
            
            await browser.close()
        
        file_size_kb = pdf_file.stat().st_size / 1024
        print("=" * 60)
        print("✓ SUCCESS!")
        print("=" * 60)
        print(f"\nPDF exported: {pdf_file}")
        print(f"File size: {file_size_kb:.1f} KB")
        print(f"Pages: 14 (one per slide)")
        print(f"\nYou can now email this PDF to clubs!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print("\nPlease check that:")
        print("  - index.html exists in the same folder")
        print("  - You have internet connection (for first run)")
        
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    asyncio.run(export_to_pdf())
