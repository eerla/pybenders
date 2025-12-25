# PyBenders 🐍

**AI-powered short-form content generator for programming MCQs and brain teasers**

PyBenders automatically generates daily video reels featuring Python quiz questions with explanations. The pipeline creates visually engaging content from question generation to final video output.

## Features

- **AI Question Generation**: Uses OpenAI GPT-4 to generate Python MCQs with explanations
- **Image Rendering**: Creates styled question/answer cards with syntax highlighting
- **Video Pipeline**: Assembles images into short-form reels with transitions
- **Batch Processing**: Generate multiple questions per run with metadata tracking
- **Modular Design**: Separate components for generation, rendering, and video assembly

## Current Focus

**Python MCQs** covering:
- Python internals & memory model
- List comprehensions & generators
- Variable scope & closures
- Mutability & immutability
- Decorators, async/await
- Threading & GIL
- Standard library gotchas
- OOP internals
- Truthiness & comparisons

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# Generate reels
python -m pybender --questions 2
```

## Project Structure

```
pybender/
├── generator/       # AI question generation
├── render/          # Image & video rendering
├── config/          # Settings & env config
├── assets/          # Fonts, backgrounds, music
└── prompts/         # LLM prompt templates

output/
├── images/          # Generated question cards
├── reels/           # Final video output
└── runs/            # Metadata per generation run
```

## Requirements

- Python 3.10+
- OpenAI API key
- FFmpeg (for video rendering)

## Future Roadmap

### Additional Programming Languages
- JavaScript/TypeScript quirks
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
