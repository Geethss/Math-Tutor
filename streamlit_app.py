import streamlit as st
import requests
import os
import time
from pathlib import Path
import base64
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="Auto Math Grader",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
# API Configuration - Use environment variable for production, localhost for development
import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_ENDPOINTS = {
    "health": f"{API_BASE_URL}/api/health",
    "analyze": f"{API_BASE_URL}/api/analyze",
    "results": f"{API_BASE_URL}/api/results"
}

def check_api_health():
    """Check if the API server is running"""
    try:
        response = requests.get(API_ENDPOINTS["health"], timeout=5)
        return response.status_code == 200
    except:
        return False

def display_header():
    """Display the main header"""
    st.markdown('<h1 class="main-header">🧮 Auto Math Grader System</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #6c757d;">
            Upload handwritten math problems and get instant AI-powered grading and analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display sidebar with instructions and status"""
    with st.sidebar:
        st.header("📋 Instructions")
        
        st.markdown("""
        **How to use:**
        1. Upload a concept sheet template
        2. Upload question images (1-5 files)
        3. Upload corresponding solution images
        4. Click "Analyze" to get results
        
        **Supported formats:**
        - JPG, JPEG, PNG, BMP, TIFF
        - Max 10MB per file
        - Max 5 question-solution pairs
        """)
        
        st.header("🔧 System Status")
        
        # Check API health
        if check_api_health():
            st.success("✅ API Server Connected")
        else:
            st.error("❌ API Server Offline")
            st.markdown("""
            **To start the server:**
            ```bash
            python start_server.py
            ```
            Or manually:
            ```bash
            uvicorn app.main:app --reload
            ```
            """)
        
        st.header("📚 Resources")
        st.markdown("""
        - [API Documentation]({API_BASE_URL}/docs)
        - [GitHub Repository](#)
        - [Report Issues](#)
        """)

def validate_uploaded_files(concept_sheet, questions, solutions):
    """Validate uploaded files"""
    errors = []
    
    # Check if files are uploaded
    if not concept_sheet:
        errors.append("Concept sheet is required")
    
    if not questions:
        errors.append("At least one question is required")
    
    if not solutions:
        errors.append("At least one solution is required")
    
    # Check file counts match
    if questions and solutions and len(questions) != len(solutions):
        errors.append("Number of questions and solutions must match")
    
    # Check maximum limit
    if questions and len(questions) > 5:
        errors.append("Maximum 5 question-solution pairs allowed")
    
    # Check file types
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
    if concept_sheet:
        ext = Path(concept_sheet.name).suffix.lower()
        if ext not in allowed_extensions:
            errors.append("Concept sheet must be an image file")
    
    for i, q in enumerate(questions or []):
        ext = Path(q.name).suffix.lower()
        if ext not in allowed_extensions:
            errors.append(f"Question {i+1} must be an image file")
    
    for i, s in enumerate(solutions or []):
        ext = Path(s.name).suffix.lower()
        if ext not in allowed_extensions:
            errors.append(f"Solution {i+1} must be an image file")
    
    return errors

def display_file_upload():
    """Display file upload interface"""
    st.header("📁 Upload Files")
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Concept Sheet")
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        concept_sheet = st.file_uploader(
            "Upload your concept sheet template",
            type=['jpg', 'jpeg', 'png', 'bmp', 'tiff'],
            key="concept_sheet",
            help="This is the template that will be filled with results"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if concept_sheet:
            st.success(f"✅ Uploaded: {concept_sheet.name}")
            # Show preview
            image = Image.open(concept_sheet)
            st.image(image, caption="Concept Sheet Preview", width='stretch')
    
    with col2:
        st.subheader("❓ Questions")
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        questions = st.file_uploader(
            "Upload question images (1-5 files)",
            type=['jpg', 'jpeg', 'png', 'bmp', 'tiff'],
            accept_multiple_files=True,
            key="questions",
            help="Upload handwritten math questions"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if questions:
            st.success(f"✅ Uploaded {len(questions)} question(s)")
            # Show previews
            for i, q in enumerate(questions[:3]):  # Show first 3
                image = Image.open(q)
                st.image(image, caption=f"Question {i+1}", width='stretch')
            if len(questions) > 3:
                st.info(f"... and {len(questions) - 3} more questions")
    
    # Solutions section
    st.subheader("✏️ Solutions")
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    solutions = st.file_uploader(
        "Upload solution images (1-5 files)",
        type=['jpg', 'jpeg', 'png', 'bmp', 'tiff'],
        accept_multiple_files=True,
        key="solutions",
        help="Upload handwritten solutions corresponding to the questions"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if solutions:
        st.success(f"✅ Uploaded {len(solutions)} solution(s)")
        # Show previews
        for i, s in enumerate(solutions[:3]):  # Show first 3
            image = Image.open(s)
            st.image(image, caption=f"Solution {i+1}", width='stretch')
        if len(solutions) > 3:
            st.info(f"... and {len(solutions) - 3} more solutions")
    
    return concept_sheet, questions, solutions

def analyze_files(concept_sheet, questions, solutions):
    """Send files to API for analysis"""
    if not check_api_health():
        st.error("❌ API server is not running. Please start the server first.")
        return None
    
    # Prepare files for API
    files = []
    
    # Add concept sheet
    if concept_sheet:
        files.append(('concept_sheet', concept_sheet))
    
    # Add questions (multiple files)
    if questions:
        for q in questions:
            files.append(('questions', q))
    
    # Add solutions (multiple files)  
    if solutions:
        for s in solutions:
            files.append(('solutions', s))
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("🔄 Sending files to API...")
        progress_bar.progress(20)
        
        # Send request to API
        response = requests.post(API_ENDPOINTS["analyze"], files=files, timeout=300)
        progress_bar.progress(80)
        
        if response.status_code == 200:
            result = response.json()
            progress_bar.progress(100)
            status_text.text("✅ Analysis completed!")
            return result
        else:
            error_msg = response.json().get('detail', 'Unknown error')
            st.error(f"❌ Analysis failed: {error_msg}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out. The analysis is taking too long.")
        return None
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
        return None
    finally:
        progress_bar.empty()
        status_text.empty()

def display_results(result):
    """Display analysis results"""
    st.header("📊 Analysis Results")
    
    if not result:
        return
    
    # Success message
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.success("🎉 Analysis completed successfully!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Create tabs for different result types
    tab1, tab2 = st.tabs(["📊 Analysis Table", "📝 Detailed Analysis"])
    
    with tab1:
        st.subheader("Analysis Results Table")
        analysis_table_url = result.get('analysis_table_url', '')
        if analysis_table_url:
            # Try to display the table
            try:
                # Extract filename from URL
                filename = analysis_table_url.split('/')[-1]
                table_url = f"{API_ENDPOINTS['results']}/{filename}"
                
                # Download and display table
                response = requests.get(table_url)
                if response.status_code == 200:
                    table_content = response.content.decode('utf-8')
                    st.markdown(table_content)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Analysis Table",
                        data=table_content,
                        file_name=filename,
                        mime="text/markdown"
                    )
                else:
                    st.error("Could not load analysis table")
            except Exception as e:
                st.error(f"Error loading table: {str(e)}")
        else:
            st.warning("No analysis table available")
    
    with tab2:
        st.subheader("Detailed Analysis Report")
        analysis_url = result.get('detailed_analysis_url', '')
        if analysis_url:
            try:
                # Extract filename from URL
                filename = analysis_url.split('/')[-1]
                text_url = f"{API_ENDPOINTS['results']}/{filename}"
                
                # Download and display text
                response = requests.get(text_url)
                if response.status_code == 200:
                    analysis_text = response.content.decode('utf-8')
                    st.text_area("Analysis Report", analysis_text, height=400)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Analysis Report",
                        data=analysis_text,
                        file_name=filename,
                        mime="text/plain"
                    )
                else:
                    st.error("Could not load analysis report")
            except Exception as e:
                st.error(f"Error loading analysis: {str(e)}")
        else:
            st.warning("No detailed analysis available")

def main():
    """Main application function"""
    display_header()
    display_sidebar()
    
    # Check if API is running
    if not check_api_health():
        st.error("""
        **API Server is not running!**
        
        Please start the server first:
        1. Open a terminal/command prompt
        2. Navigate to the project directory
        3. Run: `python start_server.py`
        4. Wait for the server to start
        5. Refresh this page
        """)
        return
    
    # File upload section
    concept_sheet, questions, solutions = display_file_upload()
    
    # Analyze button
    if st.button("🚀 Analyze Files", type="primary", width='stretch'):
        # Validate files
        errors = validate_uploaded_files(concept_sheet, questions, solutions)
        
        if errors:
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            st.error("❌ Please fix the following errors:")
            for error in errors:
                st.write(f"• {error}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Reset file pointers
            if concept_sheet:
                concept_sheet.seek(0)
            if questions:
                for q in questions:
                    q.seek(0)
            if solutions:
                for s in solutions:
                    s.seek(0)
            
            # Analyze files
            with st.spinner("🔄 Analyzing files... This may take a few minutes."):
                result = analyze_files(concept_sheet, questions, solutions)
            
            if result:
                display_results(result)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; margin-top: 2rem;">
        <p>🧮 Auto Math Grader System | Powered by Gemini AI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
