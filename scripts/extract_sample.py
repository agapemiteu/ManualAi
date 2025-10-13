#!/usr/bin/env python3
"""
Extract first 30 pages from Toyota 4Runner manual for testing.
This creates a ~1-2MB PDF for quick uploads and testing.
"""

import PyPDF2
from pathlib import Path

def extract_pages(input_pdf, output_pdf, start_page=0, end_page=30):
    """Extract specific pages from a PDF."""
    
    print(f"📄 Extracting pages {start_page+1} to {end_page} from {input_pdf.name}...")
    
    # Read the input PDF
    with open(input_pdf, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        pdf_writer = PyPDF2.PdfWriter()
        
        total_pages = len(pdf_reader.pages)
        print(f"   Total pages in original: {total_pages}")
        
        # Adjust end_page if it exceeds total pages
        end_page = min(end_page, total_pages)
        
        # Extract pages
        for page_num in range(start_page, end_page):
            pdf_writer.add_page(pdf_reader.pages[page_num])
        
        # Write the output PDF
        with open(output_pdf, 'wb') as output_file:
            pdf_writer.write(output_file)
    
    # Get file size
    size_mb = output_pdf.stat().st_size / (1024 * 1024)
    print(f"✅ Created: {output_pdf.name}")
    print(f"   Pages: {end_page - start_page}")
    print(f"   Size: {size_mb:.2f} MB")
    
    if size_mb > 20:
        print(f"   ⚠️ Warning: File is larger than 20MB limit!")
    elif size_mb > 10:
        print(f"   ⚠️ Note: File is larger than 10MB (may take 3-5 minutes to process)")
    else:
        print(f"   ✅ Perfect size for quick processing!")

if __name__ == "__main__":
    # Paths
    input_pdf = Path("data/2023-Toyota-4runner-Manual.pdf")
    output_pdf = Path("data/Toyota-4Runner-Sample-30pages.pdf")
    
    if not input_pdf.exists():
        print(f"❌ Error: {input_pdf} not found!")
        exit(1)
    
    # Extract first 30 pages (introduction, safety, basic controls)
    extract_pages(input_pdf, output_pdf, start_page=0, end_page=30)
    
    print(f"\n🚀 Ready to upload! Use: {output_pdf}")
    print(f"   Or visit: https://manual-ai-psi.vercel.app/upload")
