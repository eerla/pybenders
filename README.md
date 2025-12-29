# PyBenders 🐍

**AI-powered short-form content generator for programming MCQs and brain teasers**

PyBenders generates daily short-form reels across multiple subjects (code, SQL, regex, system design, DevOps) with question cards, answers, and explanations. The pipeline goes from LLM prompt → validation → rendered images → stitched video.

## Features

- **Multi-subject support**: Python, SQL, regex, system design, Linux, Docker/K8s, JavaScript, Rust, Go
- **AI question generation**: Subject-aware prompt templates per content type (code, SQL query, regex, scenario, command output, DevOps Q&A)
- **Validation pass**: Content-type-specific validators keep outputs within length/shape rules
- **Image rendering**: Styled question/answer cards with syntax highlighting and CTA frames
- **Video pipeline**: Assembles cards into reels with transitions; metadata tracked per run
- **Batch processing**: Generate multiple questions per run; sweep all subjects in one command

## Supported Subjects

- Python (code_output)
- JavaScript (code_output)
- Rust (code_output)
- Go (code_output)
- SQL (query_output)
- Regex (pattern_match)
- System Design (scenario)
- Linux commands (command_output)
- Docker/K8s (qa)

Each subject maps to a content type that controls the prompt, validator, and renderer.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# Generate reels for Python
python -m pybender --questions 2 --subject python

# Run a full sweep (1 question per subject)
python -m pybender
```

## Project Structure

```
pybender/
├── generator/       # Content registry, LLM orchestration, validators
├── prompts/         # Prompt templates keyed by content type
├── render/          # Image & video rendering (cards, CTA, reels)
├── config/          # Settings & env config
├── assets/          # Fonts, backgrounds, music

output/
├── images/<subject>/runs/<ts>/   # Generated question/answer cards
├── reels/<subject>/runs/<ts>/    # Final video output
└── runs/<subject>/<ts>/metadata.json  # Render manifest
```

## Pipeline (high level)

subject → content registry → content_type → prompt_templates[content_type] → LLM → validator[content_type] → renderer[content_type] → video stitcher

- Content registry: maps subjects to content types and topic pools
- Prompt templates: tailored per content type (code_output, query_output, pattern_match, scenario, command_output, qa)
- Validators: enforce field/length/shape constraints before rendering
- Renderers: build question/answer cards and CTA frames; video renderer stitches into reels

## Requirements

- Python 3.10+
- OpenAI API key
- FFmpeg (for video rendering)

## Future Roadmap

### Additional Programming Languages
- TypeScript/JavaScript quirks
- Java memory & concurrency
- C++ edge cases
- Rust ownership puzzles
- Go channels & goroutines

### New Content Genres

**Logic & Reasoning**
- Aptitude puzzles
- Pattern recognition
- Mathematical reasoning
- Brain teasers

**Technical Challenges**
- SQL query optimization
- System design mini-questions
- Database normalization puzzles
- API design scenarios

**Science & Psychology**
- Weird science facts
- Cognitive bias examples
- Psychology experiments
- Counterintuitive phenomena

**Career Development**
- Salary negotiation myths
- Tech career advice
- Interview preparation tips
- Industry insights

**Emerging Tech**
- AI-generated challenges
- Machine learning puzzles
- Algorithm visualization
- Code optimization challenges

## Outputs

- Images: saved under `output/images/<subject>/runs/<timestamp>/`
- Reels: saved under `output/reels/<subject>/runs/<timestamp>/`
- Metadata: `output/runs/<subject>/<timestamp>/metadata.json` describes generated assets

## Architecture Goals

- Plugin system for content types
- Multi-language support
- Customizable visual themes
- A/B testing framework
- Analytics integration
- Social media auto-posting

## Contributing

This project is currently in active development. Contributions welcome for:
- New question templates
- Visual design improvements
- Additional language support
- Performance optimizations

## License

MIT
