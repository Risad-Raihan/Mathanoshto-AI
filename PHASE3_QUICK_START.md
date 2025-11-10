# Phase 3: File Management - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

**For OCR Support (Optional):**
```bash
# Arch Linux
sudo pacman -S tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

### Step 2: Run Database Migration
```bash
python migrate_file_tables.py
```

This will create three new tables:
- `files` - Main file storage
- `file_tags` - Tag system
- `conversation_files` - Chat integration

### Step 3: Start the Application
```bash
streamlit run frontend/streamlit/app.py
# or
./run_app.sh
```

## 🧪 Testing the File System

### Test 1: Upload a File
1. Log in to the application
2. Click **📁** button in the sidebar
3. Go to **📤 Upload Files** tab
4. Drag and drop a PDF, DOCX, or text file
5. Click **Upload Files**
6. ✅ Verify file appears in **My Files**

### Test 2: Search Files
1. Upload 2-3 files with different content
2. Go to **🔍 Search Files** tab
3. Search for a keyword from one file
4. ✅ Verify correct file is found

### Test 3: File Q&A (RAG)
1. Upload a PDF or DOCX file
2. Go to **📂 My Files**
3. Click **🔍 View** on the file
4. Type a question about the file content
5. Click **Get Answer**
6. Copy the generated prompt
7. Go back to chat (← Back to Chat)
8. Paste the prompt in chat
9. ✅ Verify AI answers based on the file content

### Test 4: File Tags
1. View a file (🔍 View)
2. Click **✏️ Edit**
3. Add tags: `important, work, report`
4. Click **💾 Save Changes**
5. Go to **🔍 Search Files**
6. Filter by one of your tags
7. ✅ Verify file appears in results

### Test 5: File Management
1. Test **⬇️ Download** - verify file downloads correctly
2. Test **✏️ Edit** - change description and folder
3. Test **🗑️ Delete** - delete a file (with confirmation)
4. ✅ Verify all operations work

### Test 6: Storage Stats
1. Upload several files of different types
2. Go to **📊 Storage Stats** tab
3. ✅ Verify:
   - Total files count is correct
   - Storage size is shown
   - Files by type breakdown is accurate
   - Tags are listed

## 📋 Sample Test Files

Create these test files to thoroughly test the system:

### test_document.txt
```
This is a test document for the file management system.
It contains important information about AI and machine learning.
The system should be able to search and extract this text.
```

### test_data.csv
```csv
Name,Age,City
Alice,30,New York
Bob,25,Los Angeles
Charlie,35,Chicago
```

### test_config.json
```json
{
  "app_name": "File Manager Test",
  "version": "1.0.0",
  "features": ["upload", "search", "tags"],
  "max_file_size": "50MB"
}
```

## 🔍 Verification Checklist

After testing, verify these features work:

### File Upload ✅
- [ ] PDF files upload successfully
- [ ] DOCX files upload successfully
- [ ] Text files upload successfully
- [ ] CSV files upload successfully
- [ ] JSON files upload successfully
- [ ] Images upload successfully
- [ ] File size validation works
- [ ] Text extraction works
- [ ] Thumbnails are generated

### File Management ✅
- [ ] Files appear in "My Files"
- [ ] Download works correctly
- [ ] Rename works
- [ ] Delete works with confirmation
- [ ] Edit description works
- [ ] Move to folder works

### Search & Organization ✅
- [ ] Search by filename works
- [ ] Search by content works
- [ ] Filter by file type works
- [ ] Filter by tags works
- [ ] Sort options work
- [ ] Folder navigation works

### Tags ✅
- [ ] Add tags works
- [ ] Remove tags works
- [ ] Tag filtering works
- [ ] Tag statistics shown correctly

### RAG Features ✅
- [ ] File Q&A generates correct prompts
- [ ] File summarization works
- [ ] LLM uses file context correctly
- [ ] Multi-file analysis possible

### UI/UX ✅
- [ ] Thumbnails display correctly
- [ ] File cards show all info
- [ ] Icons display for file types
- [ ] Buttons are responsive
- [ ] Tabs work smoothly
- [ ] Navigation is intuitive

## 🐛 Troubleshooting

### Issue: "No module named 'pdfplumber'"
**Solution:** Run `pip install -r requirements.txt`

### Issue: "No module named 'fitz'"
**Solution:** Install PyMuPDF: `pip install PyMuPDF`

### Issue: "pytesseract not found"
**Solution:** Install tesseract system package (see Step 1)

### Issue: "Database table doesn't exist"
**Solution:** Run the migration: `python migrate_file_tables.py`

### Issue: "Permission denied when uploading"
**Solution:** Ensure `uploads/` directory exists and is writable:
```bash
mkdir -p uploads
chmod 755 uploads
```

### Issue: "Thumbnail generation fails"
**Solution:** 
- For PDFs: Ensure PyMuPDF is installed
- For images: Ensure Pillow is installed
- Fallback: Icon thumbnails will be used

### Issue: "File search doesn't find content"
**Solution:** Ensure "Extract text content" is enabled during upload

## 📊 Performance Notes

- **Upload Speed**: Depends on file size and text extraction
  - Small files (< 1MB): ~1-2 seconds
  - Medium files (1-10MB): ~3-10 seconds
  - Large files (10-50MB): ~10-30 seconds

- **Text Extraction**: 
  - TXT/CSV/JSON: Very fast (< 1s)
  - DOCX: Fast (~1-2s)
  - PDF: Moderate (~2-5s per 10 pages)
  - OCR: Slow (~5-10s per image)

- **Search Speed**: 
  - By filename: Instant
  - By content: Fast (< 1s for 100s of files)
  - By tags: Instant

## 🎯 Next Steps

After verifying all features work:

1. **Test with Real Documents**: Upload your actual PDFs, documents, and files
2. **Use in Chat**: Try asking questions about uploaded files
3. **Organize with Tags**: Create a tagging system that works for you
4. **Set Up Folders**: Organize files into virtual folders
5. **Explore RAG**: Test file Q&A and summarization features

## 💡 Pro Tips

1. **Enable text extraction** during upload for better search
2. **Use consistent tags** for better organization
3. **Add descriptions** to important files
4. **Use folders** to organize by project or topic
5. **Test file Q&A** with specific, detailed questions
6. **Disable OCR** for faster uploads (enable only when needed)

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review `PHASE3_FILE_MANAGEMENT.md` for detailed documentation
3. Check application logs in terminal
4. Verify all dependencies are installed

---

**Congratulations!** 🎉 You now have a fully functional file management system with RAG capabilities!

