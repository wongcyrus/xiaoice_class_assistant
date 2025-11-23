#!/usr/bin/env python3
"""
Import presentation cache from Excel for a specific course.
Updates Firestore and regenerates speech files if messages have changed.

Usage:
  python import_cache_from_excel.py --course-id MY_COURSE --file my_course_cache.xlsx
"""

import argparse
import logging
import sys
import os
import pandas as pd
from google.cloud import firestore

# Add path to import course_utils from backend/functions/config
# Assuming this script is in backend/admin_tools/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../functions/config')))
try:
    import course_utils
except ImportError:
    logging.error("Could not import course_utils. Make sure backend/functions/config is in python path.")
    sys.exit(1)

# Import local modules
try:
    import config
    import tts_utils
except ImportError:
    # Support running from tests/ where we need to import from admin_tools package
    from admin_tools import config
    from admin_tools import tts_utils

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def import_from_excel(course_id: str, input_file: str):
    """Import cache entries from Excel and update Firestore/TTS."""
    
    if not os.path.exists(input_file):
        logger.error(f"File not found: {input_file}")
        return

    # Get bucket name
    bucket_name = getattr(config, 'speech_file_bucket', None)
    if not bucket_name:
        logger.error("speech_file_bucket not defined in config.py")
        return

    logger.info(f"Reading {input_file}...")
    try:
        df = pd.read_excel(input_file)
    except Exception as e:
        logger.error(f"Failed to read Excel file: {e}")
        return

    # Validate columns
    required_columns = [
        "Cache Key (Do Not Edit)",
        "Generated Message (Edit this)",
        "Speaker Notes (Context)",
        "Language"
    ]
    for col in required_columns:
        if col not in df.columns:
            logger.error(f"Missing required column: {col}")
            return

    project_id = getattr(config, 'project_id', None)
    db = firestore.Client(project=project_id, database="langbridge")
    collection_ref = db.collection("langbridge_presentation_cache")
    
    updated_count = 0
    skipped_count = 0
    error_count = 0

    logger.info(f"Processing {len(df)} rows for course '{course_id}'...")

    for index, row in df.iterrows():
        cache_key = row.get("Cache Key (Do Not Edit)")
        new_message = row.get("Generated Message (Edit this)")
        context = row.get("Speaker Notes (Context)")
        language = row.get("Language")
        
        if pd.isna(cache_key) or not cache_key:
            logger.warning(f"Row {index+2}: Missing Cache Key. Skipping.")
            continue
            
        if pd.isna(new_message):
            new_message = ""
        else:
            new_message = str(new_message).strip()

        doc_ref = collection_ref.document(cache_key)
        doc = doc_ref.get()
        
        if not doc.exists:
            logger.warning(f"Row {index+2}: Cache key {cache_key} not found in Firestore. Skipping.")
            error_count += 1
            continue
            
        current_data = doc.to_dict()
        current_message = current_data.get("message", "")
        
        # Check if message changed
        if new_message == current_message:
            skipped_count += 1
            continue
            
        logger.info(f"Row {index+2}: Message changed for {cache_key}. Updating...")
        
        try:
            # 1. Regenerate Audio
            voice_params = course_utils.get_voice_params(course_id, language)
            
            # Use tts_utils to generate and upload speech
            # This uses the same filename generation logic (based on context hash)
            # so it overwrites the old file in the bucket.
            filename = tts_utils.generate_speech_file(
                bucket_name=bucket_name,
                message=new_message,
                language_code=language,
                context=context,
                voice_params=voice_params
            )
            
            new_audio_url = f"https://storage.googleapis.com/{bucket_name}/{filename}"
            
            # 2. Update Firestore
            update_data = {
                "message": new_message,
                "audio_url": new_audio_url,
                "updated_at": firestore.SERVER_TIMESTAMP
            }
            doc_ref.update(update_data)
            
            logger.info(f"  -> Updated Firestore and Audio: {filename}")
            updated_count += 1
            
        except Exception as e:
            logger.error(f"Failed to update row {index+2} ({cache_key}): {e}")
            error_count += 1

    logger.info("------------------------------------------------")
    logger.info(f"Import Complete.")
    logger.info(f"Updated: {updated_count}")
    logger.info(f"Skipped (Unchanged): {skipped_count}")
    logger.info(f"Errors: {error_count}")

def main():
    parser = argparse.ArgumentParser(description="Import presentation cache from Excel.")
    parser.add_argument("--course-id", required=True, help="Course ID (for voice config).")
    parser.add_argument("--file", required=True, help="Input Excel file path.")
    
    args = parser.parse_args()
    
    import_from_excel(args.course_id, args.file)

if __name__ == "__main__":
    main()
