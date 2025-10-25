import base64
import json
import os
from google import genai
from app.config.settings import GEMINI_API_KEY


if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_KEY_HERE":
    print("[WARNING] GEMINI_API_KEY not configured! Please set it in your .env file.")
    print("[WARNING] Get your API key from: https://aistudio.google.com/app/apikey")
    print("[WARNING] Using mock responses for testing...")

client = genai.Client(api_key=GEMINI_API_KEY)

def get_mime_type(path):
    """Get MIME type based on file extension"""
    ext = os.path.splitext(path.lower())[1]
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.tif': 'image/tiff'
    }
    return mime_types.get(ext, 'image/jpeg')  # Default to jpeg

def encode_image_b64(path):
    """Encode image to base64 string"""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def create_content_with_parsed_concepts(parsed_concepts, question, solution, prompt):
    """Create content for Gemini API with parsed concepts and images"""
    content_parts = [
        {
            "text": f"Instructions: {prompt}\n\nParsed Concept Sheet:\n{json.dumps(parsed_concepts, indent=2)}\n\nHere are the images to analyze:"
        },
        {
            "text": "Question Image:"
        },
        {
            "inline_data": {
                "mime_type": get_mime_type(question), 
                "data": encode_image_b64(question)
            }
        },
        {
            "text": "Solution Image:"
        },
        {
            "inline_data": {
                "mime_type": get_mime_type(solution),
                "data": encode_image_b64(solution)
            }
        }
    ]
    return content_parts

def call_gemini_phase1(parsed_concepts, question, solution, prompt):
    """Call Gemini API for Phase 1 analysis using parsed concepts"""
    try:
        print(f"[DEBUG] Starting Phase 1 analysis...")
        print(f"[DEBUG] Parsed concepts: {len(parsed_concepts.get('concepts', {}))} concepts")
        print(f"[DEBUG] Question: {question}")
        print(f"[DEBUG] Solution: {solution}")
        print(f"[DEBUG] API Key present: {bool(GEMINI_API_KEY and GEMINI_API_KEY != 'YOUR_KEY_HERE')}")
        
        # If no API key, return mock data for testing
        if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_KEY_HERE":
            print("[DEBUG] Using mock response for testing...")
            return {
                "concept_id": 1,
                "concept_name": "Basic Formulas",
                "question_transcription": "Solve for x: 2x + 5 = 13",
                "student_transcription": "x = 4",
                "correct_answer": "x = 4",
                "is_correct": True,
                "analysis": "Student correctly solved the equation by subtracting 5 from both sides and dividing by 2.",
                "status_summary": "Correct solution"
            }
        
        # Create content with parsed concepts and images
        content = create_content_with_parsed_concepts(parsed_concepts, question, solution, prompt)
        print(f"[DEBUG] Content created with {len(content)} parts")
        
        # Generate response using the client
        print(f"[DEBUG] Calling Gemini API...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=content
        )
        print(f"[DEBUG] Response received: {len(response.text) if hasattr(response, 'text') else 'No text'} characters")
        
        # Parse JSON response
        response_text = response.text.strip()
        print(f"[DEBUG] Raw response: {response_text[:200]}...")
        
        # Try to extract JSON from response
        json_text = response_text
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
            print(f"[DEBUG] Extracted JSON from ```json block: {json_text[:100]}...")
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
            print(f"[DEBUG] Extracted JSON from ``` block: {json_text[:100]}...")
        else:
            print(f"[DEBUG] Using full response as JSON: {json_text[:100]}...")
        
        # Parse JSON
        try:
            result = json.loads(json_text)
            print(f"[DEBUG] Successfully parsed JSON with keys: {list(result.keys())}")
            return result
        except json.JSONDecodeError as e:
            print(f"[DEBUG] JSON parsing failed: {str(e)}")
            print(f"[DEBUG] JSON text that failed: {json_text}")
            # If JSON parsing fails, return a structured error response
            return {
                "concept_id": 1,  # Provide a fallback concept ID
                "concept_name": "Unknown",
                "question_transcription": "Failed to transcribe",
                "student_transcription": "Failed to transcribe",
                "correct_answer": "Failed to generate",
                "is_correct": False,
                "analysis": f"Error parsing Gemini response: {response_text[:200]}...",
                "status_summary": "Analysis failed - JSON parsing error"
            }
            
    except Exception as e:
        print(f"[ERROR] Phase 1 failed: {str(e)}")
        error_msg = str(e)
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            error_msg = "API key not configured or invalid. Please check your GEMINI_API_KEY in .env file."
        
        return {
            "concept_id": 1,  # Provide a fallback concept ID
            "concept_name": "Unknown",
            "question_transcription": "Failed to transcribe",
            "student_transcription": "Failed to transcribe",
            "correct_answer": "Failed to generate", 
            "is_correct": False,
            "analysis": f"Error calling Gemini API: {error_msg}",
            "status_summary": f"Analysis failed - {error_msg[:50]}..."
        }

def call_gemini_phase2(parsed_concepts, phase1_results, prompt):
    """Call Gemini API for Phase 2 synthesis using parsed concepts"""
    try:
        print(f"[DEBUG] Starting Phase 2 synthesis...")
        print(f"[DEBUG] Parsed concepts: {len(parsed_concepts.get('concepts', {}))} concepts")
        print(f"[DEBUG] Phase 1 results: {len(phase1_results)} items")
        
        # If no API key, return mock data for testing
        if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_KEY_HERE":
            print("[DEBUG] Using mock synthesis response for testing...")
            return {
                "fill_data": {
                    "1": "Correct solution - Student demonstrated good understanding of algebra",
                    "2": "Needs improvement - Calculation errors in step 3"
                },
                "detailed_analysis": "Student shows strong understanding of basic algebra concepts. However, there are some calculation errors that need attention. Focus on double-checking arithmetic operations and showing all steps clearly."
            }
        
        # Create content for synthesis
        content_parts = [
            {
                "text": f"Instructions: {prompt}\n\nParsed Concept Sheet:\n{json.dumps(parsed_concepts, indent=2)}\n\nPhase 1 Results:\n{json.dumps(phase1_results, indent=2)}"
            }
        ]
        
        print(f"[DEBUG] Calling Gemini API for synthesis...")
        # Generate response using the client
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=content_parts
        )
        print(f"[DEBUG] Synthesis response received: {len(response.text) if hasattr(response, 'text') else 'No text'} characters")
        
        # Parse JSON response
        response_text = response.text.strip()
        print(f"[DEBUG] Phase 2 raw response: {response_text[:200]}...")
        
        # Try to extract JSON from response
        json_text = response_text
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
            print(f"[DEBUG] Phase 2 extracted JSON from ```json block: {json_text[:100]}...")
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
            print(f"[DEBUG] Phase 2 extracted JSON from ``` block: {json_text[:100]}...")
        else:
            print(f"[DEBUG] Phase 2 using full response as JSON: {json_text[:100]}...")
        
        # Parse JSON
        try:
            result = json.loads(json_text)
            print(f"[DEBUG] Phase 2 successfully parsed JSON with keys: {list(result.keys())}")
            return result
        except json.JSONDecodeError as e:
            print(f"[DEBUG] Phase 2 JSON parsing failed: {str(e)}")
            print(f"[DEBUG] Phase 2 JSON text that failed: {json_text}")
            # If JSON parsing fails, return a structured error response
            return {
                "fill_data": {},
                "detailed_analysis": f"Error parsing Gemini response: {response_text[:500]}..."
            }
            
    except Exception as e:
        print(f"[ERROR] Phase 2 failed: {str(e)}")
        error_msg = str(e)
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            error_msg = "API key not configured or invalid. Please check your GEMINI_API_KEY in .env file."
        
        return {
            "fill_data": {},
            "detailed_analysis": f"Error calling Gemini API: {error_msg}"
        }