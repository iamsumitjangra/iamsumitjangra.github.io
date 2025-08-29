#!/bin/bash

# Book Cover Download Script
# Downloads book covers from your Goodreads CSV export

echo "📚 Book Cover Downloader"
echo "========================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if books.csv exists
if [ ! -f "books.csv" ]; then
    echo "❌ books.csv not found in current directory."
    echo "   Please make sure you're running this from the books directory."
    exit 1
fi

# Install requirements if needed
echo "🔧 Installing Python dependencies..."
python3 -m pip install -r requirements.txt --quiet

# Create img-books directory if it doesn't exist
mkdir -p img-books

# Run the download script
echo "🚀 Starting book cover downloads..."
echo "   This may take a while depending on your library size..."
echo ""

python3 download_covers.py

echo ""
echo "✅ Download process completed!"
echo "📁 Check the img-books directory for downloaded covers."
echo "🌐 Your books page will now use local images with external fallbacks."
