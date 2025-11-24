# Migration Guide - Speaker Note Generator Refactoring

## For Developers Using This Code

This guide helps you understand the changes and migrate any custom code.

## Quick Reference: Old vs New

### Importing Utilities

#### Before
```python
# Everything was in main.py
from main import IMAGE_REGISTRY, run_stateless_agent
```

#### After
```python
# Import from specific modules
from utils.image_utils import get_image, register_image
from utils.agent_utils import run_stateless_agent
from utils.progress_utils import load_progress, save_progress
```

### Configuration

#### Before
```python
# Environment variables set directly
os.environ["SPEAKER_NOTE_PROGRESS_FILE"] = "/path/to/progress.json"
process_presentation(pptx_path, pdf_path)
```

#### After
```python
# Use Config object
from config import Config

config = Config(
    pptx_path=pptx_path,
    pdf_path=pdf_path,
    progress_file="/path/to/progress.json"
)
config.validate()
```

### Image Registry

#### Before
```python
# Global variable
IMAGE_REGISTRY[image_id] = image
img = IMAGE_REGISTRY.get(image_id)
del IMAGE_REGISTRY[image_id]
```

#### After
```python
# Functions with clear intent
from utils.image_utils import register_image, get_image, unregister_image

register_image(image_id, image)
img = get_image(image_id)
unregister_image(image_id)
```

### Progress Tracking

#### Before
```python
# Functions scattered in main.py
progress = load_progress(path)
save_progress(path, data)
key = slide_key(index, notes)
```

#### After
```python
# Import from dedicated module
from utils.progress_utils import (
    load_progress,
    save_progress,
    create_slide_key,
    get_progress_file_path
)

progress = load_progress(path)
save_progress(path, data)
key = create_slide_key(index, notes)
```

### Agent Execution

#### Before
```python
# Helper functions in main.py
result = await run_stateless_agent(agent, prompt, images)
img_bytes = await run_visual_agent(agent, prompt, images)
```

#### After
```python
# Import from agent_utils
from utils.agent_utils import run_stateless_agent, run_visual_agent

result = await run_stateless_agent(agent, prompt, images)
img_bytes = await run_visual_agent(agent, prompt, images)
```

### Creating Agent Tools

#### Before
```python
# Tools defined inline in process_presentation()
async def call_analyst(image_id: str) -> str:
    image = IMAGE_REGISTRY.get(image_id)
    # ... implementation
```

#### After
```python
# Use tool factory
from tools.agent_tools import AgentToolFactory

factory = AgentToolFactory(
    analyst_agent=analyst_agent,
    writer_agent=writer_agent,
    auditor_agent=auditor_agent
)

call_analyst = factory.create_analyst_tool()
speech_writer = factory.create_writer_tool(theme, global_context)
call_auditor = factory.create_auditor_tool()
```

### Visual Generation

#### Before
```python
# Visual generation logic mixed in main loop
if not skip_visuals:
    # 100 lines of visual generation code
    img_bytes = await run_visual_agent(...)
    with open(img_path, "wb") as f:
        f.write(img_bytes)
    # Embed in presentation
    new_slide = prs.slides.add_slide(...)
```

#### After
```python
# Use VisualGenerator service
from services.visual_generator import VisualGenerator

generator = VisualGenerator(
    designer_agent=designer_agent,
    output_dir=config.visuals_dir,
    skip_generation=config.skip_visuals
)

img_bytes = await generator.generate_visual(
    slide_idx, slide_image, speaker_notes, retry_errors
)

if img_bytes:
    generator.add_visual_to_presentation(
        prs, slide_idx, img_path, speaker_notes
    )
```

### Main Processing Flow

#### Before
```python
# Everything in one big function
async def process_presentation(pptx_path, pdf_path, course_id, skip_visuals):
    # 500 lines of processing logic
    # Load files
    # Generate global context
    # Configure tools
    # Process slides
    # Save presentation
```

#### After
```python
# Use PresentationProcessor service
from services.presentation_processor import PresentationProcessor

async def process_presentation(pptx_path, pdf_path, course_id, skip_visuals):
    config = Config(
        pptx_path=pptx_path,
        pdf_path=pdf_path,
        course_id=course_id,
        skip_visuals=skip_visuals
    )
    
    processor = PresentationProcessor(
        config=config,
        supervisor_agent=supervisor_agent,
        analyst_agent=analyst_agent,
        writer_agent=writer_agent,
        auditor_agent=auditor_agent,
        overviewer_agent=overviewer_agent,
        designer_agent=designer_agent
    )
    
    return await processor.process()
```

## Common Patterns

### Pattern 1: Testing Utilities

#### Before
```python
# Hard to test without full integration
# Had to import entire main.py

import main
# Can't mock dependencies easily
```

#### After
```python
# Easy to test individual utilities
from utils.progress_utils import create_slide_key

def test_slide_key_generation():
    key = create_slide_key(1, "test notes")
    assert key.startswith("slide_1_")
    assert len(key.split("_")) == 3

# Can mock dependencies
from unittest.mock import Mock
from services.visual_generator import VisualGenerator

async def test_visual_skip():
    mock_agent = Mock()
    generator = VisualGenerator(
        mock_agent, "/output", skip_generation=True
    )
    result = await generator.generate_visual(1, image, "notes")
    assert result is None
```

### Pattern 2: Adding New Features

#### Before
```python
# Had to modify main.py directly
# Risk breaking existing functionality

async def process_presentation(...):
    # Add new code here
    # Mixed with existing logic
```

#### After
```python
# Create new service or utility
# main.py remains unchanged

# services/summarizer.py
class SummarizerService:
    def __init__(self, config):
        self.config = config
    
    async def summarize(self, slides):
        # Implementation

# Then use it
from services.summarizer import SummarizerService

summarizer = SummarizerService(config)
summary = await summarizer.summarize(slides)
```

### Pattern 3: Configuration Changes

#### Before
```python
# Environment variables scattered throughout
os.environ["GOOGLE_CLOUD_LOCATION"] = region
os.environ["SPEAKER_NOTE_PROGRESS_FILE"] = progress_file
os.environ["SPEAKER_NOTE_RETRY_ERRORS"] = "true"
```

#### After
```python
# Centralized in Config class
config = Config(
    pptx_path=pptx_path,
    pdf_path=pdf_path,
    progress_file=progress_file,
    retry_errors=True,
    region=region
)

# Config handles environment variables internally
```

## Breaking Changes

### None!

The CLI interface is **100% backward compatible**:

```bash
# All existing commands work unchanged
python main.py --pptx input.pptx --pdf input.pdf
python main.py --pptx input.pptx --pdf input.pdf --course-id CS101
python main.py --pptx input.pptx --pdf input.pdf --skip-visuals
python main.py --pptx input.pptx --pdf input.pdf --retry-errors --region us-central1
```

### What Changed Internally

1. **File organization** - Code split into modules
2. **Import paths** - Utilities now in dedicated modules
3. **Architecture** - Service-oriented design

### What Didn't Change

1. **CLI interface** - Same arguments, same behavior
2. **Agent definitions** - agents/ directory unchanged
3. **Output format** - Same enhanced PPTX files
4. **Progress files** - Same JSON format
5. **Visual files** - Same PNG files in visuals/

## Troubleshooting

### ImportError: No module named 'config'

**Problem:** Python can't find new modules

**Solution:** Make sure you're running from the correct directory
```bash
cd backend/speaker_note_generator
python main.py --pptx input.pptx --pdf input.pdf
```

### AttributeError: module 'main' has no attribute 'IMAGE_REGISTRY'

**Problem:** Old code trying to access global variable

**Solution:** Update imports
```python
# Old
from main import IMAGE_REGISTRY

# New
from utils.image_utils import get_image, register_image
```

### TypeError: Config() missing required argument

**Problem:** Forgot to pass required config parameters

**Solution:** Check Config class signature
```python
config = Config(
    pptx_path=pptx_path,  # Required
    pdf_path=pdf_path,    # Required
    course_id=None,       # Optional
    skip_visuals=False    # Optional
)
```

## Best Practices

### 1. Import Specific Functions

```python
# Good
from utils.image_utils import register_image, get_image

# Avoid
from utils.image_utils import *
```

### 2. Use Type Hints

```python
# Good
async def process_slide(slide_idx: int, image: Image.Image) -> str:
    pass

# Less clear
async def process_slide(slide_idx, image):
    pass
```

### 3. Inject Dependencies

```python
# Good
processor = PresentationProcessor(
    config=config,
    supervisor_agent=supervisor_agent
)

# Avoid
# Creating dependencies inside class
```

### 4. Test Individual Components

```python
# Good - Test specific utility
from utils.progress_utils import create_slide_key

def test_slide_key():
    key = create_slide_key(1, "notes")
    assert key.startswith("slide_1_")

# Avoid - Only testing full integration
```

## Getting Help

### Understanding the Architecture

1. Read `ARCHITECTURE.md` for visual diagrams
2. Read `REFACTORING.md` for detailed documentation
3. Read `REFACTORING_SUMMARY.md` for quick overview

### Code Examples

Each module has docstrings with examples:

```python
from utils.image_utils import register_image

help(register_image)
# Shows:
# register_image(image_id: str, image: Image.Image) -> None
#     Register an image in the global registry.
```

### Module Purpose

| Module | Purpose | When to Use |
|--------|---------|-------------|
| `config.py` | Configuration | Need to manage settings |
| `utils/image_utils.py` | Image handling | Working with slide images |
| `utils/progress_utils.py` | Progress tracking | Save/load progress |
| `utils/agent_utils.py` | Agent execution | Run agents |
| `tools/agent_tools.py` | Tool creation | Create supervisor tools |
| `services/presentation_processor.py` | Main workflow | Process presentations |
| `services/visual_generator.py` | Visual generation | Generate enhanced slides |

## Examples

### Example 1: Custom Progress Storage

```python
from utils.progress_utils import load_progress, save_progress

# Use custom progress file
progress_path = "/custom/path/progress.json"
progress = load_progress(progress_path)

# Modify progress
progress["custom_field"] = "value"

# Save atomically
save_progress(progress_path, progress)
```

### Example 2: Custom Visual Processing

```python
from services.visual_generator import VisualGenerator

class CustomVisualGenerator(VisualGenerator):
    async def generate_visual(self, slide_idx, slide_image, notes, retry):
        # Custom processing
        img_bytes = await super().generate_visual(
            slide_idx, slide_image, notes, retry
        )
        
        # Apply watermark
        if img_bytes:
            img_bytes = self.add_watermark(img_bytes)
        
        return img_bytes
    
    def add_watermark(self, img_bytes):
        # Watermark implementation
        return img_bytes

# Use custom generator
generator = CustomVisualGenerator(
    designer_agent, output_dir, skip_generation=False
)
```

### Example 3: Custom Agent Tool

```python
from tools.agent_tools import AgentToolFactory

class CustomToolFactory(AgentToolFactory):
    def create_summarizer_tool(self):
        async def summarize_slide(content: str) -> str:
            """Tool: Summarizes slide content."""
            prompt = f"Summarize this: {content}"
            return await run_stateless_agent(
                self.summarizer_agent, prompt
            )
        return summarize_slide

# Use custom factory
factory = CustomToolFactory(
    analyst_agent, writer_agent, auditor_agent
)
```

## Summary

The refactoring makes the codebase:

✅ **More maintainable** - Clear module boundaries
✅ **More testable** - Independent components
✅ **More extensible** - Easy to add features
✅ **More readable** - Focused, small modules
✅ **100% compatible** - No breaking changes

All while keeping the CLI interface exactly the same!
