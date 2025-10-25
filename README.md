# Auto Math Grader System (Gemini-Powered)

### Overview
A fully automated system that grades handwritten math problems, fills the concept sheet, and generates a detailed analysis report using Gemini API. Perfect for educators who want to automate math grading without technical complexity.

---

### 🚀 Features
- **🌐 User-Friendly Interface:** Beautiful Streamlit frontend for non-technical users
- **📱 Drag & Drop Upload:** Simple file upload with live previews
- **🤖 AI-Powered Grading:** Uses Gemini 1.5 Pro for intelligent analysis
- **📊 Real-Time Progress:** Live progress bars and status updates
- **📋 Auto-Fill Reports:** Automatically fills concept sheet with status summaries
- **📝 Detailed Insights:** Generates comprehensive text analysis reports
- **🔧 Smart Validation:** File type, size, and count validation
- **📡 REST API:** Full API access for developers and integrations

---

### 🧩 Tech Stack
- **Backend:** FastAPI with automatic API documentation
- **AI:** Google Gemini 1.5 Pro for math analysis
- **Image Processing:** OpenCV for cropping + Pillow for rendering
- **Validation:** Comprehensive file type and size validation
- **Error Handling:** Detailed error messages and graceful failure handling

---

### 🚀 Quick Start

#### 1. Installation
```bash
git clone <repo-url>
cd Math-tutor
pip install -r requirements.txt
```

#### 2. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your Gemini API credentials
# GEMINI_API_KEY=your_actual_api_key_here
# GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent
```

#### 3. Run the System

**Option A: Streamlit Frontend (Recommended)**
```bash
# Start both API server and Streamlit frontend
python start_streamlit.py

# Or use the batch file (Windows)
start_streamlit.bat

# Or use the shell script (Unix/Linux/Mac)
./start_streamlit.sh
```

**Option B: API Server Only**
```bash
# Start just the API server
python start_server.py

# Or manually
uvicorn app.main:app --reload
```

#### 4. Access the System

**With Streamlit Frontend:**
- 🌐 **Streamlit App:** http://localhost:8501 (User-friendly interface)
- 📡 **API Server:** http://localhost:8000 (Backend)
- 📚 **API Docs:** http://localhost:8000/docs (Technical documentation)

**API Only:**
- 📡 **API Server:** http://localhost:8000
- 📚 **API Docs:** http://localhost:8000/docs

#### 5. Test the System
```bash
# Run the test suite
python test_api.py
```

---

### 🌐 Streamlit Frontend

The Streamlit frontend provides a beautiful, user-friendly interface for non-technical users:

#### Key Features:
- **📁 Drag & Drop Upload:** Easy file selection with live previews
- **📊 Progress Tracking:** Real-time progress bars during analysis
- **📋 Results Display:** Interactive tabs for filled concept sheet and analysis
- **🔧 Smart Validation:** Automatic file validation with helpful error messages
- **📥 Download Results:** One-click download of generated files

#### How to Use:
1. **Start the System:** Run `python start_streamlit.py`
2. **Open Browser:** Navigate to http://localhost:8501
3. **Upload Files:** Drag and drop your concept sheet, questions, and solutions
4. **Click Analyze:** Watch the progress bar as AI processes your files
5. **View Results:** Download the filled concept sheet and detailed analysis

#### Interface Preview:
```
🧮 Auto Math Grader System
├── 📋 Upload Concept Sheet
├── ❓ Upload Questions (1-5 files)
├── ✏️ Upload Solutions (1-5 files)
├── 🚀 Analyze Button
└── 📊 Results Display
    ├── 📋 Filled Concept Sheet
    └── 📝 Detailed Analysis Report
```

---

### 📖 API Usage

#### Basic Analysis Request
```python
import requests

files = {
    'concept_sheet': open('concept_sheet.jpg', 'rb'),
    'questions': [open('question1.jpg', 'rb'), open('question2.jpg', 'rb')],
    'solutions': [open('solution1.jpg', 'rb'), open('solution2.jpg', 'rb')]
}

response = requests.post('http://localhost:8000/api/analyze', files=files)
result = response.json()

# Access results
print(f"Filled concept sheet: {result['filled_concept_sheet_url']}")
print(f"Analysis report: {result['detailed_analysis_url']}")
```

#### Using curl
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "concept_sheet=@concept_sheet.jpg" \
  -F "questions=@question1.jpg" \
  -F "questions=@question2.jpg" \
  -F "solutions=@solution1.jpg" \
  -F "solutions=@solution2.jpg"
```

---

### 🔧 System Architecture

```
📁 Math-tutor/
├── 📁 app/
│   ├── 📁 config/          # Configuration settings
│   ├── 📁 data/            # Coordinates template
│   ├── 📁 prompts/         # AI prompts for grading
│   ├── 📁 routes/          # API endpoints
│   ├── 📁 services/        # Core processing logic
│   └── 📁 static/output/   # Generated results
├── 📁 sample_images/       # Test images directory
├── 📄 .env.example         # Environment template
├── 📄 API_DOCUMENTATION.md # Complete API docs
├── 📄 test_api.py         # Test suite
└── 📄 requirements.txt    # Dependencies
```

### 🔄 Processing Pipeline

1. **File Upload & Validation** → Check file types, sizes, counts
2. **Image Preprocessing** → Crop individual problems using OpenCV
3. **Phase 1 Analysis** → Grade each problem with Gemini AI
4. **Phase 2 Synthesis** → Generate comprehensive analysis
5. **Output Generation** → Create filled concept sheet + text report

---

### 📋 Requirements

- **Python 3.8+**
- **Gemini API Key** (get from Google AI Studio)
- **Image files** in supported formats (JPG, PNG, BMP, TIFF)
- **Maximum 10MB** per file, **5 question-solution pairs** max

---

### 🛠️ Configuration

#### Environment Variables (.env)
```env
# Get your API key from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

#### Coordinates Template (app/data/coords_template.json)
Maps concept IDs to coordinates on your concept sheet for automatic filling:
```json
{
  "1": [50, 100, 200, 30],
  "2": [50, 150, 200, 30],
  "3": [50, 200, 200, 30]
}
```

---

### 🧪 Testing

#### Run Test Suite
```bash
python test_api.py
```

#### Manual Testing
1. Add sample images to `sample_images/` directory
2. Start the server: `uvicorn app.main:app --reload`
3. Visit `http://localhost:8000/docs` for interactive API documentation
4. Test the `/api/analyze` endpoint with your images

---

### 📚 Documentation

- **[API Documentation](API_DOCUMENTATION.md)** - Complete API reference
- **[Sample Images](sample_images/README.md)** - Test image requirements
- **Interactive Docs** - Visit `http://localhost:8000/docs` when server is running

---

### 🚨 Troubleshooting

#### Common Issues
- **"File not found" errors:** Check that result files exist in `app/static/output/`
- **Gemini API errors:** Verify API key and URL in `.env` file
- **Image processing errors:** Ensure images are valid and not corrupted
- **Memory issues:** Large images may cause processing delays

#### Debug Mode
Check server logs for detailed error information.

---

### 🎯 Perfect For

- **Math Teachers** - Automate grading of handwritten homework
- **Tutoring Centers** - Generate detailed student progress reports  
- **Educational Researchers** - Analyze student error patterns
- **Assessment Companies** - Scale math problem evaluation

---

### 📄 License

This project is open source. See LICENSE file for details.