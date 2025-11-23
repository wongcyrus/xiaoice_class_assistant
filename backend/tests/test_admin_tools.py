import os
import sys
import pytest
import pandas as pd
import uuid
import time
from google.cloud import firestore

# Add backend directory to path so we can import admin_tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from admin_tools import export_cache_to_excel
from admin_tools import import_cache_from_excel
from admin_tools import config

# Use a unique course ID for this test run to avoid collisions
TEST_COURSE_ID = f"test_course_{str(uuid.uuid4())[:8]}"
TEST_EXCEL_FILE = f"test_cache_{str(uuid.uuid4())[:8]}.xlsx"

@pytest.fixture(scope="module")
def db():
    """Return a real Firestore client connected to the project."""
    project_id = getattr(config, 'project_id', None)
    if not project_id:
        pytest.skip("Project ID not found in config.py")
    return firestore.Client(project=project_id, database="langbridge")

@pytest.fixture(scope="module")
def setup_test_data(db):
    """Create a seed cache entry in Firestore."""
    collection_ref = db.collection("langbridge_presentation_cache")
    
    # Unique cache key
    context_hash = "testhash123"
    cache_key = f"v1:en:{context_hash}"
    
    data = {
        "message": "Original Message",
        "language_code": "en",
        "context": "Test Context",
        "context_hash": context_hash,
        "course_ids": [TEST_COURSE_ID],
        "audio_url": "http://original-url",
        "updated_at": firestore.SERVER_TIMESTAMP
    }
    
    doc_ref = collection_ref.document(cache_key)
    doc_ref.set(data)
    
    yield cache_key
    
    # Cleanup
    doc_ref.delete()
    if os.path.exists(TEST_EXCEL_FILE):
        os.remove(TEST_EXCEL_FILE)

def test_export_and_import_cycle(db, setup_test_data):
    """
    Integration Test:
    1. Export the seeded data to Excel.
    2. Verify Excel content.
    3. Modify Excel (change message).
    4. Import back to Firestore.
    5. Verify Firestore update (Message change & Audio URL change).
    """
    cache_key = setup_test_data
    
    # --- Step 1: Export ---
    print(f"Exporting cache for course {TEST_COURSE_ID}...")
    export_cache_to_excel.export_to_excel(TEST_COURSE_ID, TEST_EXCEL_FILE)
    
    assert os.path.exists(TEST_EXCEL_FILE), "Export file was not created"
    
    # --- Step 2: Verify Export ---
    df = pd.read_excel(TEST_EXCEL_FILE)
    assert len(df) == 1, "Expected exactly 1 row in exported Excel"
    row = df.iloc[0]
    assert row["Cache Key (Do Not Edit)"] == cache_key
    assert row["Generated Message (Edit this)"] == "Original Message"
    
    # --- Step 3: Modify Excel ---
    new_message = f"Updated Message {uuid.uuid4()}"
    df.at[0, "Generated Message (Edit this)"] = new_message
    df.to_excel(TEST_EXCEL_FILE, index=False)
    print(f"Modified Excel with new message: {new_message}")
    
    # --- Step 4: Import ---
    # Note: This will trigger TTS generation. 
    # Ensure config.speech_file_bucket is set and accessible.
    print("Importing modified Excel...")
    import_cache_from_excel.import_from_excel(TEST_COURSE_ID, TEST_EXCEL_FILE)
    
    # --- Step 5: Verify Firestore Update ---
    doc_ref = db.collection("langbridge_presentation_cache").document(cache_key)
    doc = doc_ref.get()
    assert doc.exists
    data = doc.to_dict()
    
    assert data["message"] == new_message, "Firestore message was not updated"
    assert data["audio_url"] != "http://original-url", "Audio URL should have been updated"
    assert "speech_en" in data["audio_url"], "Audio URL should contain generated filename"
    
    print("Test cycle completed successfully!")