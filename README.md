# PyBenders 🐍

**AI-powered short-form content generator for Instagram Reels and Carousels**

PyBenders generates daily programming MCQs and brain teasers across multiple subjects (Python, SQL, regex, system design, DevOps, mind benders) with AI-generated questions, beautiful carousel/reel cards, video reels, and automated Instagram upload. The pipeline goes from LLM prompt → validation → rendered images → dual-format generation (reel + carousel) → video stitching → Instagram publishing.

## Features

### Content Generation
- **Multi-subject support**: Python, SQL, regex, system design, Linux, Docker/K8s, JavaScript, Rust, Go, mind benders (brain teasers)
- **AI question generation**: Subject-aware LLM prompts with validation for content quality
- **Dual-format rendering**: Both reel (1080×1920) and carousel (1080×1080) images generated per question
- **Carousel format**: 6-slide Instagram carousels for technical subjects (cover, question, countdown, answer, explanation, CTA)
- **Mind benders format**: 5-card carousel with colorful themes (welcome, question, hint, answer, CTA)
- **Video reels**: Two types - technical content (with countdown transitions) and mind benders (5-image sequence without transitions)
- **Batch processing**: Generate 1-10+ questions per run; multi-subject sweeps in one command

### Instagram Publishing
- **Unified upload pipeline**: Single function handles both carousel albums and reel videos
- **Session persistence**: Reuses saved sessions to avoid repeated logins and Instagram security blocks
- **Human-like behavior**: Random delays between uploads to mimic real user activity
- **Automatic organization**: Successfully uploaded files auto-organized by date in `uploaded/` folder
- **Error handling**: Detailed logging and retry logic for failed uploads
- **Custom thumbnails**: Question images as reel thumbnails

### Rendering & Styling
- **Styled cards**: Question/answer/explanation cards with syntax highlighting
- **Responsive layout**: Adapts to different content lengths
- **Subject headers**: Each slide displays subject name for context
- **Scenario support**: Question and answer slides support scenario labels
- **CTA frame**: Call-to-action slide for engagement

## Supported Subjects

| Subject | Content Type | Example |
|---------|-------------|---------|
| Python | code_output | What's the output? |
| JavaScript | code_output | Async/await edge cases |
| Rust | code_output | Ownership & borrowing |
| Go | code_output | Goroutines & channels |
| SQL | query_output | Query optimization |
| Regex | pattern_match | Pattern matching |
| System Design | scenario | Design a scalable API |
| Linux | command_output | Bash command puzzles |
| Docker/K8s | qa | Container orchestration Q&A |
| Mind Benders | mind_bender | Logic puzzles, riddles, brain teasers |

Each subject maps to a content type that controls the LLM prompt, validator rules, and renderer styling. Mind benders use a unique colorful theme-based renderer with 5 rotating color palettes (sunset, ocean, mint, lavender, golden).

## Quick Start

### Setup

```bash
# Clone and install
cd pybenders
python -m venv .venv
.venv\Scripts\activate  # or: source .venv/bin/activate on macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your:
# - OPENAI_API_KEY (for content generation)
# - INSTAGRAM_USERNAME (for publishing)
# - INSTAGRAM_PASSWORD (for publishing)

# Install FFmpeg (required for video rendering)
# Windows: choco install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

### Generate Content

```bash
# Generate 2 Python questions with carousels and reels
python -m pybender --subject python --questions 2

# Generate 1 question from each supported subject
python -m pybender

# List all available commands
python -m pybender --help
```

### Upload to Instagram

```bash
# Upload most recent carousel and reel to Instagram
# (automatically uses saved session, reuses across runs)
python -m pybender upload

# Or upload specific metadata file
python -m pybender upload path/to/metadata.json
```

### Output Structure

**Generated content:**
```
output_1/
├── python/
│   ├── carousels/              # 6-slide carousel images
│   ├── images/                 # Question/answer/explanation images
│   └── reels/                  # Video files
└── runs/
    └── 2026-01-01_205914_metadata.json  # Content manifest

**Published content:**
```
uploaded/
├── python/
│   └── 2026-01-01_205914/
│       ├── carousels/          # Moved after successful upload
│       └── reels/              # Moved after successful upload
```

## Project Structure

```
pybender/
├── __main__.py              # CLI entry point
├── config/
│   ├── logging_config.py
│   └── settings.py
├── generator/
│   ├── content_registry.py  # Subject → content type mapping
│   ├── question_gen.py      # LLM orchestration
│   └── schema.py            # Content validation schemas
├── prompts/
│   └── templates.py         # Subject-specific LLM prompts
├── render/
│   ├── carousel.py          # 6-slide carousel generation
│   ├── image.py             # Question/answer/explanation cards
│   ├── video.py             # Reel video stitching
│   ├── code_renderer.py     # Syntax highlighting
│   ├── text_utils.py        # Text layout utilities
│   └── layout_*.py          # Layout profiles
├── publishers/
│   └── instagram_publisher.py  # Upload & session management
└── assets/
    ├── backgrounds/         # Image backgrounds
    ├── fonts/              # Font files
    └── music/              # Background music
```

## Pipeline Overview

### Content Generation Pipeline
```
Subject → Content Registry → LLM Prompt → Validation → Approved ✓
                                             ↓
                                          Rejected ✗ (retry)
```

1. **Content Registry**: Maps subject → content type → topic pool
2. **LLM Prompt**: Subject-specific prompt from `prompts/templates.py`
3. **Validation**: Content-type-specific validators ensure quality
4. **Retry Logic**: Failed validations trigger automatic retries

### Rendering Pipeline
```
Approved Content → Image Rendering → Carousel Generation → Video Stitching → Metadata
```

1. **Image Rendering** (`render/image.py`):
   - Generate question card with subject header
   - Generate answer card (highlight correct option)
   - Generate explanation card (show answer + explanation)

2. **Carousel Generation** (`render/carousel.py`):
   - Creates 6-slide carousel:
     - Slide 1: Welcome/cover
     - Slide 2: Question with subject header
     - Slide 3: Countdown timer
     - Slide 4: Answer with subject header
     - Slide 5: Explanation with subject header
     - Slide 6: Call-to-action

3. **Video Stitching** (`render/video.py`):
   - Assembles images into video reel
   - Adds smooth transitions and fades
   - Includes background music (4.8s + 7s + explanation)
   - 1080×1920 vertical format for Instagram Reels

4. **Metadata**: JSON manifest with all asset paths for upload

### Instagram Upload Pipeline
```
Metadata JSON → Login (with session) → Upload Carousels → Wait 12s → Upload Reels → Organize Files
```

1. **Session Management** (`publishers/instagram_publisher.py`):
   - Loads saved session from `sessions/instagram_session_*.json`
   - Validates with lightweight user info check
   - Performs fresh login only if needed
   - Saves session for next run (avoids Instagram security blocks)

2. **Carousel Upload**:
   - Uploads 6 images as Instagram album
   - Auto-captions with subject hashtags
   - 10-15s random delays between posts

3. **Strategic Delays**:
   - 1s before session validation
   - 3s before fresh login
   - 3s after login before save
   - 12s between carousel and reel batches
   - 10-15s between individual uploads

4. **Reel Upload**:
   - Uploads video with custom thumbnail (question image)
   - Auto-captions with subject hashtags
   - Same delay strategy as carousels

5. **File Organization**:
   - Successfully uploaded carousels → `uploaded/<subject>/<run_date>/carousels/`
   - Successfully uploaded reels → `uploaded/<subject>/<run_date>/reels/`

## Requirements

- **Python**: 3.10+
- **OpenAI API key**: For LLM-based question generation
- **FFmpeg**: For video rendering (crucial!)
- **Instagram Account**: For publishing
- **RAM**: 4GB+ recommended (8GB+ if running with parallel video processing)

### Installation

```bash
# Windows
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

## Best Practices

### Memory Management
- The project now includes proper MoviePy cleanup to release video memory
- If you encounter memory errors while generating videos:
  - Close unnecessary applications (VS Code uses ~3GB, Chrome uses ~250MB)
  - Set `max_workers=1` in `render/video.py` line 352 for sequential processing
  - Generate fewer questions at once: `python -m pybender --questions 1`

### Instagram Session Management
- Sessions are saved to `sessions/instagram_session_<username>.json`
- First upload creates the session, subsequent uploads reuse it
- Never manually logout - sessions expire naturally and are refreshed on next run
- If you get blocked, wait 15-30 minutes and try again
- Follows [instagrapi best practices](https://subzeroid.github.io/instagrapi/usage-guide/best-practices.html)

### Rate Limiting
- Includes human-like random delays (10-15s between uploads)
- Respects Instagram's rate limits
- Don't run multiple upload sessions simultaneously

## Future Roadmap

### Phase 1: Platform Expansion
- [ ] TikTok upload support (different video format)
- [ ] YouTube Shorts support
- [ ] LinkedIn article generation (long-form from questions)
- [ ] Twitter/X thread generation

### Phase 2: Advanced Generation
- [ ] Multi-language support (Spanish, Hindi, French)
- [ ] Domain-specific variants (Data Science, DevOps, Cloud Architecture)
- [ ] Difficulty levels (Beginner, Intermediate, Advanced)
- [ ] Interactive quiz format (with polls, A/B/C/D buttons)

### Phase 3: Analytics & Optimization
- [ ] Engagement tracking from Instagram API
- [ ] A/B testing different carousel formats
- [ ] Best time to post analysis
- [ ] Subject popularity metrics
- [ ] Viewer retention analytics

### Phase 4: Content Management
- [ ] Web UI for question/answer editing before upload
- [ ] Scheduled posting (daily/weekly automation)
- [ ] Content calendar view
- [ ] Bulk upload from CSV
- [ ] Content approval workflow

### Phase 5: Monetization Features
- [ ] Patreon integration for exclusive content
- [ ] Course generation from questions
- [ ] AI tutor chatbot for follow-up explanations
- [ ] Affiliate link integration

## Troubleshooting

### Memory Errors During Video Generation
**Error**: `numpy._core._exceptions._ArrayMemoryError: Unable to allocate X MiB`

**Solutions**:
1. Close VS Code and other RAM-heavy applications
2. Reduce parallel processing: Change `max_workers=2` to `max_workers=1` in `render/video.py`
3. Generate fewer questions: `python -m pybender --questions 1`
4. Restart your computer to clear fragmented memory

### Instagram Login Fails
**Error**: `Login failed: Sorry, there was a problem with your request.` (HTTP 400)

**Solutions**:
1. Verify credentials in `.env` file
2. Check if account requires 2FA - complete login in Instagram app first
3. Wait 15-30 minutes - Instagram may have rate-limited your account
4. Delete corrupted session: Remove `sessions/instagram_session_*.json`
5. Try again with fresh login

### Session Logout During Upload
**Error**: `user_has_logged_out` during upload

**Solutions**:
1. This happens when Instagram invalidates the session
2. Delete session file and run again for fresh login
3. Ensure 12-second delay between carousel and reel uploads is respected
4. Reduce batch size to 1-2 questions per run

### FFmpeg Not Found
**Error**: `FileNotFoundError: ffmpeg not found`

**Solutions**:
1. Install FFmpeg (see Requirements section above)
2. Add FFmpeg to system PATH
3. Verify: `ffmpeg -version` in terminal

## Architecture & Design Decisions

### Session Persistence Strategy
Rather than generating a fresh session for each upload, PyBenders:
- Saves session to disk after login
- Reuses saved session in next run
- Only performs fresh login if saved session is invalid
- Never manually logs out - lets sessions expire naturally

This approach minimizes Instagram's detection of suspicious activity and avoids repeated login attempts.

### Memory Management in Video Rendering
MoviePy doesn't automatically release memory, so PyBenders:
- Explicitly closes all video/audio clips after rendering
- Forces garbage collection between videos
- Limits concurrent video processing (configurable `max_workers`)
- Allows processing adjustment based on available system RAM

### Carousel Format Decisions
The 6-slide carousel was chosen for:
- Instagram algorithm optimization (more swipes = higher engagement)
- Content storytelling (setup → question → countdown → answer → explanation → CTA)
- Question readability on mobile devices
- Ample space for syntax highlighting in code questions
- Clear visual hierarchy with subject headers on each slide

## Contributing

This project is in active development! Contributions welcome for:

- **New question templates**: Add subjects in `prompts/templates.py`
- **Rendering improvements**: Enhanced carousel styling in `render/carousel.py`
- **Platform support**: New publishers (TikTok, YouTube Shorts) in `publishers/`
- **Validator enhancements**: Stricter quality checks in `generator/schema.py`
- **Performance optimizations**: Video rendering, LLM caching, parallel processing
- **Bug fixes**: Memory issues, Instagram API changes, file path handling
- **Documentation**: Clearer setup guides, API docs, examples

## Project Status

- ✅ Question generation (LLM + validation)
- ✅ Image rendering (question/answer/explanation cards)
- ✅ Carousel generation (6-slide format with subject headers)
- ✅ Video stitching (with transitions and music)
- ✅ Instagram carousel upload
- ✅ Instagram reel upload
- ✅ Session persistence (instagrapi best practices)
- ✅ File organization (auto-organize by date)
- ✅ Memory management (proper MoviePy cleanup)
- 🔄 Metadata validation improvements
- 🔄 Enhanced error recovery
- ❌ Web UI (planned Phase 3)
- ❌ TikTok/YouTube support (planned Phase 2)
- ❌ Scheduled posting (planned Phase 4)

## License

MIT - See LICENSE file for details

## References

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [instagrapi Best Practices](https://subzeroid.github.io/instagrapi/usage-guide/best-practices.html)
- [MoviePy Documentation](https://zulko.github.io/moviepy/)
- [Pillow Image Library](https://python-pillow.org/)
