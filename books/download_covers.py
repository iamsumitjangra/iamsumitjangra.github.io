#!/usr/bin/env python3
"""
Book Cover Downloader for Goodreads CSV Export
Downloads book covers from multiple sources and saves them locally
"""

import csv
import os
import requests
import time
import re
from urllib.parse import quote
from pathlib import Path
import json

class BookCoverDownloader:
    def __init__(self, csv_file='books.csv', output_dir='img-books'):
        self.csv_file = csv_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create a log file for tracking downloads
        self.log_file = self.output_dir / 'download_log.json'
        self.download_log = self.load_log()
        
        # Request session for better performance
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def load_log(self):
        """Load existing download log"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {'downloaded': {}, 'failed': {}, 'stats': {'total': 0, 'success': 0, 'failed': 0}}
    
    def save_log(self):
        """Save download log"""
        with open(self.log_file, 'w') as f:
            json.dump(self.download_log, f, indent=2)
    
    def clean_isbn(self, isbn):
        """Clean ISBN from Goodreads format"""
        if not isbn:
            return ''
        return re.sub(r'^="?|"?$', '', isbn).strip()
    
    def generate_filename(self, book_id, title):
        """Generate consistent filename for book cover"""
        if book_id:
            return f"{book_id}.jpg"
        
        # Generate from title if no book_id
        clean_title = re.sub(r'[^a-z0-9\s]', '', title.lower())
        clean_title = re.sub(r'\s+', '-', clean_title)
        return f"{clean_title[:50]}.jpg"
    
    def get_cover_urls(self, isbn, book_id, title):
        """Generate list of cover URLs to try"""
        urls = []
        
        if isbn and len(isbn) >= 10:
            clean_isbn = re.sub(r'[^0-9X]', '', isbn)
            
            # Open Library (usually best quality)
            urls.append(f"https://covers.openlibrary.org/b/isbn/{clean_isbn}-L.jpg")
            urls.append(f"https://covers.openlibrary.org/b/isbn/{clean_isbn}-M.jpg")
            
            # Google Books
            urls.append(f"https://books.google.com/books/content?id=&printsec=frontcover&img=1&zoom=1&imgtk={clean_isbn}")
        
        # If we have Goodreads book ID, try their image
        if book_id:
            urls.append(f"https://images-na.ssl-images-amazon.com/images/P/{book_id}.01.L.jpg")
        
        return urls
    
    def download_image(self, url, filepath):
        """Download image from URL"""
        try:
            response = self.session.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Check if it's actually an image (not a 1x1 pixel or error page)
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type.lower():
                return False
            
            # Check content length (avoid tiny placeholder images)
            content_length = int(response.headers.get('content-length', 0))
            if content_length > 0 and content_length < 1000:  # Less than 1KB is likely a placeholder
                return False
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify the downloaded file is reasonable size
            if filepath.stat().st_size < 1000:
                filepath.unlink()  # Delete tiny files
                return False
            
            return True
            
        except Exception as e:
            print(f"  Error downloading {url}: {e}")
            return False
    
    def process_books(self):
        """Process all books from CSV and download covers"""
        books_processed = 0
        books_downloaded = 0
        
        print(f"📚 Reading books from {self.csv_file}")
        
        with open(self.csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Only process books that have been read
                if row.get('Exclusive Shelf') != 'read' or not row.get('Date Read'):
                    continue
                
                books_processed += 1
                title = row.get('Title', '').strip()
                book_id = row.get('Book Id', '').strip()
                isbn = self.clean_isbn(row.get('ISBN', ''))
                
                if not title:
                    continue
                
                filename = self.generate_filename(book_id, title)
                filepath = self.output_dir / filename
                
                # Skip if already downloaded successfully
                if filename in self.download_log['downloaded']:
                    print(f"✅ Skipping {title} (already downloaded)")
                    continue
                
                # Skip if we've already failed multiple times
                if filename in self.download_log['failed'] and self.download_log['failed'][filename] >= 3:
                    print(f"❌ Skipping {title} (failed too many times)")
                    continue
                
                print(f"\n📖 Processing: {title}")
                print(f"   Book ID: {book_id}, ISBN: {isbn}")
                
                # Get potential cover URLs
                cover_urls = self.get_cover_urls(isbn, book_id, title)
                
                downloaded = False
                for i, url in enumerate(cover_urls):
                    print(f"   Trying source {i+1}/{len(cover_urls)}: {url[:60]}...")
                    
                    if self.download_image(url, filepath):
                        print(f"   ✅ Downloaded successfully!")
                        self.download_log['downloaded'][filename] = {
                            'title': title,
                            'book_id': book_id,
                            'isbn': isbn,
                            'url': url,
                            'timestamp': time.time()
                        }
                        books_downloaded += 1
                        downloaded = True
                        break
                    else:
                        print(f"   ❌ Failed")
                
                if not downloaded:
                    print(f"   ❌ All sources failed for: {title}")
                    if filename not in self.download_log['failed']:
                        self.download_log['failed'][filename] = 0
                    self.download_log['failed'][filename] += 1
                
                # Save progress periodically
                if books_processed % 10 == 0:
                    self.save_log()
                
                # Be nice to the servers
                time.sleep(0.5)
        
        # Final save
        self.download_log['stats'] = {
            'total': books_processed,
            'success': books_downloaded,
            'failed': books_processed - books_downloaded,
            'last_run': time.time()
        }
        self.save_log()
        
        print(f"\n🎉 Download complete!")
        print(f"   📊 Total books processed: {books_processed}")
        print(f"   ✅ Successfully downloaded: {books_downloaded}")
        print(f"   ❌ Failed downloads: {books_processed - books_downloaded}")
        print(f"   📁 Images saved to: {self.output_dir}")

if __name__ == "__main__":
    downloader = BookCoverDownloader()
    downloader.process_books()
