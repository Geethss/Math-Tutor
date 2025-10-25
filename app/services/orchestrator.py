import os
import json
import time
from app.services.preprocessing import crop_blocks, pair_by_order
from app.services.gemini_client import call_gemini_phase1, call_gemini_phase2
from app.services.render import generate_analysis_table
from app.services.concept_parser import parse_concept_sheet
from app.config.settings import PHASE1_PROMPT_PATH, PHASE2_PROMPT_PATH, STATIC_OUTPUT_DIR

def read_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def run_pipeline(concept_sheet: str, questions: list[str], solutions: list[str]):
    print(f"[DEBUG] Starting pipeline with concept sheet: {concept_sheet}")
    print(f"[DEBUG] Concept sheet exists: {os.path.exists(concept_sheet)}")
    if os.path.exists(concept_sheet):
        print(f"[DEBUG] Concept sheet size: {os.path.getsize(concept_sheet)} bytes")
    
    # Step 0: Parse concept sheet first (FOUNDATION)
    print("[STEP 0] Parsing concept sheet...")
    parsed_concepts = parse_concept_sheet(concept_sheet)
    print(f"[DEBUG] Parsed concepts: {len(parsed_concepts.get('concepts', {}))} concepts")
    
    if parsed_concepts.get('error'):
        print(f"[ERROR] Concept sheet parsing failed: {parsed_concepts['error']}")
        return {"analysis_table": None, "analysis_path": None}
    
    phase1_prompt = read_prompt(PHASE1_PROMPT_PATH)
    phase2_prompt = read_prompt(PHASE2_PROMPT_PATH)

    # Step 1: crop all question and solution sheets (each may have multiple problems)
    all_q_crops, all_s_crops = [], []
    for i, (q, s) in enumerate(zip(questions, solutions), start=1):
        try:
            print(f"[Preprocessing] Processing question-solution pair {i}")
            print(f"[Preprocessing] Question file: {q}")
            print(f"[Preprocessing] Solution file: {s}")
            q_crops = crop_blocks(q, os.path.join(STATIC_OUTPUT_DIR, f"tmp_q_{i}"))
            s_crops = crop_blocks(s, os.path.join(STATIC_OUTPUT_DIR, f"tmp_s_{i}"))
            print(f"[Preprocessing] Extracted {len(q_crops)} question crops: {q_crops}")
            print(f"[Preprocessing] Extracted {len(s_crops)} solution crops: {s_crops}")
            all_q_crops.extend(q_crops)
            all_s_crops.extend(s_crops)
        except Exception as e:
            print(f"[Preprocessing] Error processing pair {i}: {str(e)}")
            import traceback
            traceback.print_exc()
            # Skip this pair if preprocessing fails
            continue

    print(f"[Preprocessing] Total question crops: {len(all_q_crops)}")
    print(f"[Preprocessing] Total solution crops: {len(all_s_crops)}")
    
    # If preprocessing fails, use original images as fallback
    if len(all_q_crops) == 0 or len(all_s_crops) == 0:
        print("[FALLBACK] Using original images instead of crops")
        pairs = list(zip(questions, solutions))
    else:
        pairs = pair_by_order(all_q_crops, all_s_crops)
    
    print(f"[Preprocessing] Created {len(pairs)} question-solution pairs")

    # Step 2: Phase 1 Grading Loop
    phase1_results = []
    if len(pairs) == 0:
        print("[ERROR] No question-solution pairs found! Cannot proceed with analysis.")
        return {"analysis_table": None, "analysis_path": None}
    
    for i, (qpath, spath) in enumerate(pairs, start=1):
        try:
            print(f"[Phase1] Evaluating problem {i}")
            print(f"[Phase1] Question: {qpath}")
            print(f"[Phase1] Solution: {spath}")
            result = call_gemini_phase1(parsed_concepts, qpath, spath, phase1_prompt)
            print(f"[Phase1] Result for problem {i}: {result}")
            phase1_results.append(result)
        except Exception as e:
            print(f"[Phase1] Error evaluating problem {i}: {str(e)}")
            import traceback
            traceback.print_exc()
            phase1_results.append({
                "concept_id": None,
                "concept_name": "",
                "is_correct": False,
                "status_summary": f"Error grading problem {i}: {str(e)}"
            })
        time.sleep(0.5)

    # Step 3: Phase 2 - Synthesis
    print("[Phase2] Generating final analysis...")
    print(f"[DEBUG] Phase 1 results for synthesis: {len(phase1_results)} items")
    for i, result in enumerate(phase1_results):
        print(f"[DEBUG] Result {i+1}: concept_id={result.get('concept_id')}, status_summary={result.get('status_summary', 'N/A')[:50]}...")
    
    final = call_gemini_phase2(parsed_concepts, phase1_results, phase2_prompt)
    print(f"[DEBUG] Phase 2 final result: {final}")

    os.makedirs(STATIC_OUTPUT_DIR, exist_ok=True)
    fill_data = final.get("fill_data", {})
    print(f"[DEBUG] Fill data extracted: {fill_data}")
    print(f"[DEBUG] Fill data keys: {list(fill_data.keys())}")
    
    # Generate analysis table using parsed concepts
    analysis_table_path = os.path.join(STATIC_OUTPUT_DIR, "analysis_table.md")
    analysis_text_path = os.path.join(STATIC_OUTPUT_DIR, "detailed_analysis.txt")

    print(f"[DEBUG] Generating analysis table...")
    generate_analysis_table(concept_sheet, phase1_results, fill_data, analysis_table_path, parsed_concepts)
    print(f"[DEBUG] Analysis table saved to: {analysis_table_path}")

    with open(analysis_text_path, "w", encoding="utf-8") as f:
        f.write(final.get("detailed_analysis", ""))

    return {"analysis_table": analysis_table_path, "analysis_path": analysis_text_path}
