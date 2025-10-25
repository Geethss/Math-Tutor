# Sample Images Directory

This directory should contain test images for the Auto Math Grader API.

## Required Files for Testing

Place the following files in this directory to test the API:

1. **concept_sheet.jpg** - A blank concept sheet template
2. **question1.jpg** - A handwritten math question
3. **solution1.jpg** - The corresponding handwritten solution

## Optional Additional Files

For more comprehensive testing, you can add:
- **question2.jpg, solution2.jpg** - Additional question-solution pairs
- **question3.jpg, solution3.jpg** - Up to 5 pairs maximum

## Image Requirements

- **Format:** JPG, JPEG, PNG, BMP, or TIFF
- **Size:** Maximum 10MB per file
- **Content:** Clear, readable handwritten math problems and solutions

## Usage

Once you have the sample images, run the test script:

```bash
python test_api.py
```

This will test the API endpoints and verify the system is working correctly.
