# Book Cover Download System

This system downloads book covers from your Goodreads CSV export and serves them as static files for better performance and reliability.

## Quick Start

1. **Run the download script:**
   ```bash
   ./download_covers.sh
   ```

2. **That's it!** Your books page will now use local images with external API fallbacks.

## How It Works

### Current Implementation
- **Primary**: Tries to load book covers from local `img-books/` directory
- **Fallback**: If local image fails, falls back to external APIs (Open Library, Google Books)
- **Final Fallback**: Placeholder image with book title

### Files Created
- `img-books/` - Directory containing downloaded book covers
- `img-books/download_log.json` - Log of successful/failed downloads
- `download_covers.py` - Python script that handles the downloading
- `requirements.txt` - Python dependencies

## Benefits

✅ **Faster Loading** - Local images load much faster than external APIs  
✅ **Better Reliability** - No dependency on external services being up  
✅ **Consistent Experience** - All covers load successfully  
✅ **Offline Capable** - Works without internet for cover images  
✅ **Smart Fallbacks** - Still works if local images are missing  

## Technical Details

### Cover Sources (in order of preference)
1. **Local Static Files** (`img-books/bookid.jpg`)
2. **Open Library API** (high quality covers)
3. **Google Books API** (good coverage)
4. **Placeholder Images** (generated with book title)

### File Naming Convention
- Books with Goodreads ID: `{book_id}.jpg`
- Books without ID: `{clean-title-slug}.jpg`

### Download Process
- Only processes books marked as "read" in your CSV
- Tries multiple sources for each book
- Skips already downloaded covers
- Logs all attempts for debugging
- Rate-limited to be respectful to APIs

## Maintenance

### Re-download All Covers
```bash
rm -rf img-books/
./download_covers.sh
```

### Download Only New Books
Just run the script again - it automatically skips existing covers:
```bash
./download_covers.sh
```

### Check Download Status
```bash
cat img-books/download_log.json
```

## Troubleshooting

### No Covers Downloaded
- Check that `books.csv` is in the same directory
- Ensure you have internet connection
- Check `img-books/download_log.json` for error details

### Some Covers Missing
- This is normal - not all books have covers available
- The page will automatically fall back to external APIs
- You can manually add covers to `img-books/` directory

### Script Fails
- Make sure Python 3 is installed: `python3 --version`
- Install dependencies manually: `pip3 install requests`
- Check file permissions: `chmod +x download_covers.sh`

## Customization

### Add Custom Covers
1. Save image as `img-books/{book_id}.jpg` or `img-books/{title-slug}.jpg`
2. Image should be roughly 300x400 pixels for best results
3. Supported formats: JPG, PNG (will be served as-is)

### Modify Download Sources
Edit `download_covers.py` and modify the `get_cover_urls()` method to add new sources or change priority.

---

**Note**: The download process respects API rate limits and includes delays between requests to be a good citizen of the web.
