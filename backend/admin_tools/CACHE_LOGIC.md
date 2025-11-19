# Cache Logic - Content-Based Caching (Order-Independent)

## The Problem with Slide Numbers
- Slide numbers break when slides are reordered
- Inserting a new slide shifts all numbers
- Cache becomes invalid after any reorganization

## The Solution (Content-Based Caching)

### Cache Key Formula
```
cache_key = v1:{language}:{hash(speaker_notes_content)}
```

**No slide numbers!** Only the actual speaker notes content matters.

### Flow

#### 1. **Preload** (Admin runs once per presentation)
```bash
python preload_presentation_messages.py --pptx deck.pptx --languages en,zh
```

**What it does:**
- Reads PPTX file
- For EACH slide with speaker notes:
  - Extracts the speaker notes content
  - Generates AI message from notes
  - Caches with key: `v1:en:{hash(notes_content)}`
  
Example output:
```
Slide 1: Processing 250 chars of notes
  [en] Cached 'v1:en:a1b2c3d4e5f6'
       -> Welcome to today's AI presentation...

Slide 2: Processing 180 chars of notes
  [en] Cached 'v1:en:x9y8z7w6v5u4'
       -> In this section, we'll explore...

Slide 3: Processing 250 chars of notes (duplicate content)
  [en] Cached 'v1:en:a1b2c3d4e5f6' (same hash as slide 1)
       -> Welcome to today's AI presentation...
```

#### 2. **VBA** (Runtime - when slide changes)

VBA event handler extracts current slide's notes:

```vba
' User navigates to a slide (any position in deck)
slideNum = ExtractSlideNumber(presentation)

' Get notes for current slide
slideNotes = GetNotesText(Slides(slideNum))

' Send ONLY the notes content (no slide number)
POST /api/config
{
  "generate_presentation": true,
  "languages": ["en", "zh"],
  "context": "This slide covers advanced topics..."
}
```

#### 3. **main.py** (Cloud Function)
```python
context = request_json.get("context", "")  # Just the speaker notes
generated = generate_presentation_message(lang, context)
```

**What it does:**
- Receives speaker notes content only
- Looks up cache: `v1:en:{hash(notes_content)}`
- **Cache hit!** ✅ Returns preloaded message
- Works regardless of which slide position this is

### Key Advantages

#### ✅ **Reorder-Proof**
```
Original: Slide 1 (notes A) → Slide 2 (notes B) → Slide 3 (notes C)
Cache:    hash(A)           → hash(B)           → hash(C)

Reordered: Slide 1 (notes C) → Slide 2 (notes A) → Slide 3 (notes B)
Cache:     hash(C) ✅         → hash(A) ✅         → hash(B) ✅
Still works!
```

#### ✅ **Insert-Proof**
```
Original: Slide 1 → Slide 2 → Slide 3
Insert new slide at position 2

New order: Slide 1 → [NEW] → Slide 2 → Slide 3
Cache still works for slides 1, 2, 3 (now at positions 1, 3, 4)
```

#### ✅ **Duplicate-Smart**
```
If Slide 5 has same notes as Slide 2:
- Both use same cache entry
- Only generated once during preload
- Efficient storage
```

### Testing

1. **Preload presentation:**
   ```bash
   python preload_presentation_messages.py --pptx test.pptx --languages en
   ```

2. **Reorder slides in PowerPoint** (move slide 3 to position 1)

3. **Start presentation** - cache still works! ✅

4. **Check logs:**
   ```
   INFO:✅ Cache hit for en (notes: This slide covers...)
   ```

### Cache Key Example

**Speaker Notes:**
```
This slide introduces the concept of machine learning 
and its applications in modern technology.
```

**Normalized:**
```
This slide introduces the concept of machine learning and its applications in modern technology.
```

**Hash (first 12 chars of SHA256):**
```
a7f3c8d9e2b1
```

**Cache Key:**
```
v1:en:a7f3c8d9e2b1
```

**Result:** This same content will always produce the same cache key, **no matter which slide number it's on!** 🎯
