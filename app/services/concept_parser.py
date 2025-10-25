import base64
import json
import os
from google import genai
from app.config.settings import GEMINI_API_KEY

# Initialize the Gemini client
if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_KEY_HERE":
    print("[WARNING] GEMINI_API_KEY not configured! Please set it in your .env file.")
    print("[WARNING] Get your API key from: https://aistudio.google.com/app/apikey")
    print("[WARNING] Using mock concept parsing for testing...")

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

def parse_concept_sheet(concept_sheet_path):
    """
    Parse the concept sheet to extract all concepts with their details.
    This is the foundation of the entire system.
    """
    try:
        print(f"[DEBUG] Parsing concept sheet: {concept_sheet_path}")
        print(f"[DEBUG] API Key present: {bool(GEMINI_API_KEY and GEMINI_API_KEY != 'YOUR_KEY_HERE')}")
        
        # If no API key, return mock data for testing
        if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_KEY_HERE":
            print("[DEBUG] Using mock concept sheet parsing for testing...")
            return {
                "concepts": {
                    "1": {
                        "id": 1,
                        "name": "Basic Formulas",
                        "description": "Basic integration formulas",
                        "example": "∫ x^n dx = x^(n+1)/(n+1) + C"
                    },
                    "2": {
                        "id": 2,
                        "name": "Application of Formulae",
                        "description": "Applying basic formulas",
                        "example": "Direct application of power rule"
                    }
                },
                "total_concepts": 2
            }
        
        # Create content for concept sheet parsing
        content_parts = [
            {
                "text": """You are an expert educational analyst. Your task is to parse a concept sheet and extract all concepts with their details.

CRITICAL: This is the FOUNDATION of the entire grading system. You must extract ALL concepts with 100% accuracy.

SYSTEMATIC EXTRACTION PROCESS:

STEP 1 - SCAN THE ENTIRE SHEET:
- Identify all rows/entries in the concept sheet table
- Count the total number of concepts present
- Note the structure: concept number, name, description, example columns

STEP 2 - EXTRACT EACH CONCEPT PRECISELY:
For EVERY concept in the sheet, extract:
- Concept Number/ID (e.g., 1, 2, 3, etc.)
- Concept Name (EXACT text as written - do not modify or abbreviate)
- Concept Description/Explanation (complete text from the sheet)
- Examples (any mathematical examples or formulas shown)

STEP 3 - VERIFY COMPLETENESS:
- Ensure you captured ALL concepts from top to bottom
- Double-check that concept numbers are sequential or match the sheet
- Verify that ALL fields are captured for each concept

STEP 4 - FORMAT AS JSON:
Return a structured JSON with ALL concepts organized by their ID numbers.

Critical Requirements:
- Extract EVERY SINGLE concept from the sheet (do not skip any)
- Use EXACT concept names as written (preserve capitalization, spacing, terminology)
- Include complete descriptions and examples
- If a field is empty or missing, use an empty string ""
- Never invent or modify concept names

Return JSON in this exact format:
{
  "concepts": {
    "1": {
      "id": 1,
      "name": "exact concept name from sheet",
      "description": "complete description text",
      "example": "example formulas or problems"
    },
    "2": {
      "id": 2,
      "name": "exact concept name from sheet",
      "description": "complete description text",
      "example": "example formulas or problems"
    },
    ...continue for ALL concepts...
  },
  "total_concepts": <total number of concepts extracted>
}"""
            },
            {
                "text": "Concept Sheet Image:"
            },
            {
                "inline_data": {
                    "mime_type": get_mime_type(concept_sheet_path),
                    "data": encode_image_b64(concept_sheet_path)
                }
            }
        ]
        
        print(f"[DEBUG] Calling Gemini API for concept sheet parsing...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=content_parts
        )
        print(f"[DEBUG] Concept parsing response received: {len(response.text) if hasattr(response, 'text') else 'No text'} characters")
        
        # Parse JSON response
        response_text = response.text.strip()
        print(f"[DEBUG] Raw concept parsing response: {response_text[:200]}...")
        
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
            
            # Handle both list and dict formats
            if isinstance(result, list):
                # Convert list format to our expected dict format
                concepts_dict = {}
                for concept in result:
                    concept_id = str(concept.get('concept_number', concept.get('id', '')))
                    concepts_dict[concept_id] = {
                        'id': concept.get('concept_number', concept.get('id', '')),
                        'name': concept.get('concept_name', concept.get('name', '')),
                        'description': concept.get('concept_description', concept.get('description', '')),
                        'example': concept.get('examples', concept.get('example', ''))
                    }
                result = {
                    'concepts': concepts_dict,
                    'total_concepts': len(concepts_dict)
                }
            elif isinstance(result, dict) and 'concepts' not in result:
                # If it's a dict but not in our format, try to extract concepts
                concepts_dict = {}
                for key, value in result.items():
                    if isinstance(value, dict) and 'name' in value:
                        concepts_dict[key] = value
                result = {
                    'concepts': concepts_dict,
                    'total_concepts': len(concepts_dict)
                }
            
            print(f"[DEBUG] Successfully parsed concept sheet with {len(result.get('concepts', {}))} concepts")
            return result
        except json.JSONDecodeError as e:
            print(f"[DEBUG] JSON parsing failed: {str(e)}")
            print(f"[DEBUG] JSON text that failed: {json_text}")
            # Return error structure
            return {
                "concepts": {},
                "total_concepts": 0,
                "error": f"Failed to parse concept sheet: {str(e)}"
            }
            
    except Exception as e:
        print(f"[ERROR] Concept sheet parsing failed: {str(e)}")
        error_msg = str(e)
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            error_msg = "API key not configured or invalid. Please check your GEMINI_API_KEY in .env file."
        
        return {
            "concepts": {},
            "total_concepts": 0,
            "error": f"Error parsing concept sheet: {error_msg}"
        }

def get_concept_by_id(concepts_data, concept_id):
    """Get a specific concept by ID from parsed concepts"""
    concepts = concepts_data.get("concepts", {})
    return concepts.get(str(concept_id), None)

def get_all_concept_ids(concepts_data):
    """Get all concept IDs from parsed concepts"""
    concepts = concepts_data.get("concepts", {})
    return sorted([int(k) for k in concepts.keys()], key=int)

def get_concept_name(concepts_data, concept_id):
    """Get concept name by ID"""
    concept = get_concept_by_id(concepts_data, concept_id)
    return concept.get("name", f"Concept {concept_id}") if concept else f"Concept {concept_id}"
