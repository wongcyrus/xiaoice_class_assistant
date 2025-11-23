#!/usr/bin/env python3
"""
Export presentation cache to Excel for a specific course.

Usage:
  python export_cache_to_excel.py --course-id MY_COURSE --output my_course_cache.xlsx
"""

import argparse
import logging
import sys
import pandas as pd
from google.cloud import firestore

# Import config to get project_id
try:
    import config
except ImportError:
    from admin_tools import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def export_to_excel(course_id: str, output_file: str, language: str = None):
    """Export cache entries for a course to Excel."""
    
    project_id = getattr(config, 'project_id', None)
    db = firestore.Client(project=project_id, database="langbridge")
    collection_ref = db.collection("langbridge_presentation_cache")
    
    query = collection_ref.where("course_ids", "array_contains", course_id)
    
    if language:
        query = query.where("language_code", "==", language.lower())
        
    logger.info(f"Fetching cache entries for course '{course_id}'...")
    
    docs = list(query.stream())
    logger.info(f"Found {len(docs)} entries.")
    
    if not docs:
        logger.warning("No entries found. Exiting.")
        return

    data = []
    for doc in docs:
        doc_data = doc.to_dict()
        entry = {
            "Cache Key (Do Not Edit)": doc.id,
            "Language": doc_data.get("language_code", ""),
            "Speaker Notes (Context)": doc_data.get("context", ""),
            "Generated Message (Edit this)": doc_data.get("message", ""),
            "Audio URL": doc_data.get("audio_url", ""),
            "Context Hash": doc_data.get("context_hash", "")
        }
        data.append(entry)
        
    df = pd.DataFrame(data)
    
    # Reorder columns
    columns = [
        "Cache Key (Do Not Edit)",
        "Language", 
        "Speaker Notes (Context)", 
        "Generated Message (Edit this)", 
        "Audio URL",
        "Context Hash"
    ]
    # Ensure all columns exist
    for col in columns:
        if col not in df.columns:
            df[col] = ""
            
    df = df[columns]
    
    logger.info(f"Writing to {output_file}...")
    df.to_excel(output_file, index=False)
    logger.info("Done.")

def main():
    parser = argparse.ArgumentParser(description="Export presentation cache to Excel.")
    parser.add_argument("--course-id", required=True, help="Course ID to filter by.")
    parser.add_argument("--output", default="cache_export.xlsx", help="Output Excel file path.")
    parser.add_argument("--language", help="Optional language code to filter by.")
    
    args = parser.parse_args()
    
    export_to_excel(args.course_id, args.output, args.language)

if __name__ == "__main__":
    main()
