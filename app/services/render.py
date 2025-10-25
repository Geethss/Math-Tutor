import json
import os

def generate_analysis_table(concept_sheet_path, phase1_results, fill_data, out_path, parsed_concepts=None):
    """Generate a table that matches the concept sheet structure with Status column filled"""
    print(f"[DEBUG] Render: Generating concept sheet table...")
    print(f"[DEBUG] Render: Phase 1 results: {len(phase1_results)} items")
    print(f"[DEBUG] Render: Fill data: {fill_data}")
    
    # Create the concept sheet table structure
    table_data = []
    
    # Add header matching the concept sheet format
    table_data.append("| Concept No. | Concept (With Explanation) | Example | Status |")
    table_data.append("|-------------|----------------------------|---------|--------|")
    
    # Get all concept IDs from parsed concepts (FOUNDATION)
    if parsed_concepts and 'concepts' in parsed_concepts:
        all_concept_ids = sorted([int(k) for k in parsed_concepts['concepts'].keys()], key=int)
        print(f"[DEBUG] Render: Processing concepts from parsed sheet: {all_concept_ids}")
    else:
        # Fallback to fill_data if no parsed concepts
        all_concept_ids = sorted([int(k) for k in fill_data.keys()], key=int)
        print(f"[DEBUG] Render: Processing concepts from fill_data: {all_concept_ids}")
    
    # Add each concept with its details and status
    for concept_id in all_concept_ids:
        concept_id_str = str(concept_id)
        status = fill_data.get(concept_id_str, 'No status available')
        
        # Get concept name from parsed concepts (PRIORITY)
        if parsed_concepts and 'concepts' in parsed_concepts and concept_id_str in parsed_concepts['concepts']:
            concept_display = parsed_concepts['concepts'][concept_id_str]['name']
        else:
            # Fallback to Phase 1 results or generic name
            concept_result = None
            for result in phase1_results:
                if str(result.get('concept_id', '')) == concept_id_str:
                    concept_result = result
                    break
            
            if concept_result and concept_result.get('concept_name') != 'No matching concept':
                concept_name = concept_result.get('concept_name', f'Concept {concept_id}')
                concept_display = concept_name
            else:
                # For concepts not tested, use generic name
                concept_display = f'Concept {concept_id}'
        
        # Clean up text for table formatting
        status_clean = status.replace('\n', ' ').replace('|', '-')
        
        # Truncate long text for better table display
        if len(status_clean) > 80:
            status_clean = status_clean[:77] + "..."
        
        # Add row to table - preserve original concept structure
        table_data.append(f"| {concept_id} | {concept_display} | See analysis | {status_clean} |")
    
    # Join the table
    table_content = "\n".join(table_data)
    
    # Save to file
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Concept Analysis Results\n\n")
        f.write("This table shows the analysis of each concept from the concept sheet with the Status column filled based on student performance.\n\n")
        f.write(table_content)
        f.write("\n\n## Detailed Analysis\n\n")
        f.write("See detailed_analysis.txt for comprehensive report.")
    
    print(f"[DEBUG] Render: Concept sheet table saved to {out_path}")
    return out_path
