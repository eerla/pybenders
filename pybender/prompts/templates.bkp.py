PROMPT_TEMPLATES = {
    "code_output": """
                    You are a Senior {{subject}} expert creating SHORT-FORM content for Instagram reels.

                    Generate {{n}} tricky {{subject}} multiple-choice questions about {{topic}}.

                    STRICT RULES (must follow):
                    - Return ONLY valid JSON
                    - No text outside JSON
                    - Keep content concise and reel-friendly
                    - Do NOT exceed length limits below

                    Each question MUST contain:
                    - title: max 8 words
                    - code: max 8 lines, no comments, no blank lines
                    - question: exactly 1 sentence
                    - options: exactly 4 items, each under 60 characters
                    - correct: one of "A", "B", "C", "D"
                    - explanation: max 2 short sentences, under 180 characters total

                    Additional constraints:
                    - Avoid long variable names
                    - Avoid nested examples or edge-case-heavy code
                    - Prefer clarity over completeness
                    - Assume viewer has intermediate {{subject}} knowledge
                    - Before responding, verify that every field obeys the length limits.
                    If any limit is exceeded, shorten it.
                    - Code must fit within a single screen on a mobile device.
                    - Explanation should sound like a spoken voiceover, not documentation.

                    JSON format:
                    [
                    {
                        "id": "q01",
                        "title": "...",
                        "code": "...",
                        "question": "...",
                        "options": ["...", "...", "...", "..."],
                        "correct": "B",
                        "explanation": "..."
                    }
                    ]
                    """,

    "query_output": """
                    You are a Senior {{subject}} (SQL) expert creating SHORT-FORM content for Instagram reels.

                    Generate {{n}} bite-sized SQL multiple-choice questions about {{topic}}.

                    STRICT RULES (must follow):
                    - Return ONLY valid JSON
                    - No text outside JSON
                    - Keep content concise and reel-friendly
                    - Do NOT exceed length limits below

                    Each question MUST contain:
                    - title: max 8 words
                    - schema: concise table definitions (<= 3 tables, <= 120 chars)
                    - query: max 6 lines, no comments; avoid long CTE chains
                    - code: copy the query here for rendering (same as query)
                    - question: exactly 1 sentence, under 120 characters
                    - options: exactly 4 items, each under 60 characters
                    - correct: one of "A", "B", "C", "D"
                    - explanation: max 2 short sentences, under 180 characters total

                    Additional constraints:
                    - Prefer portable SQL (ANSI over vendor-specific features)
                    - Keep data realistic but simple (small schemas, short identifiers)
                    - Avoid giant SELECT lists; focus on reasoning about result shape
                    - If a limit is exceeded, shorten it before responding

                    JSON format:
                    [
                    {
                        "id": "q01",
                        "title": "...",
                        "schema": "CREATE TABLE ...",
                        "query": "SELECT ...",
                        "code": "SELECT ...",
                        "question": "...",
                        "options": ["...", "...", "...", "..."],
                        "correct": "C",
                        "explanation": "..."
                    }
                    ]
                    """,

    "pattern_match": """
                    You are a Senior {{subject}} (regex) expert creating SHORT-FORM content for Instagram reels.

                    Generate {{n}} regex pattern-matching multiple-choice questions about {{topic}}.

                    STRICT RULES (must follow):
                    - Return ONLY valid JSON
                    - No text outside JSON
                    - Keep content concise and reel-friendly
                    - Do NOT exceed length limits below

                    Each question MUST contain:
                    - title: max 6 words
                    - input: single-line test string, under 80 characters
                    - regex: under 40 characters, no verbose mode
                    - code: 1–3 lines showing how the regex is applied
                    - question: exactly 1 sentence, under 140 characters
                    - options: exactly 4 items, each under 60 characters
                    - correct: one of "A", "B", "C", "D"
                    - explanation: max 2 short sentences, under 160 characters total

                    Additional constraints:
                    - Avoid exotic backreferences that hurt readability
                    - Prefer lookarounds only when essential
                    - If any limit is exceeded, shorten it before responding

                    JSON format:
                    [
                    {
                        "id": "q01",
                        "title": "...",
                        "input": "...",
                        "regex": "...",
                        "code": "import re\\nbool(re.search(r'...', '...'))",
                        "question": "...",
                        "options": ["...", "...", "...", "..."],
                        "correct": "A",
                        "explanation": "..."
                    }
                    ]
                    """,

    "scenario": """
                You are a Senior {{subject}} (system design) expert creating SHORT-FORM content for Instagram reels.

                Generate {{n}} lightweight system design scenarios about {{topic}}.

                STRICT RULES (must follow):
                - Return ONLY valid JSON
                - No text outside JSON
                - Keep content concise and reel-friendly
                - Do NOT exceed length limits below

                Each question MUST contain:
                - title: max 8 words
                - scenario: concise setup/requirements, under 120 characters
                - code: leave as an empty string ("") for this content type
                - question: exactly 1 sentence, under 220 characters
                - options: exactly 4 items, each under 80 characters
                - correct: one of "A", "B", "C", "D"
                - explanation: max 2 short sentences, under 200 characters total

                Additional constraints:
                - Focus on trade-offs (scalability, latency, consistency, cost)
                - Avoid deep dives; keep it single-screen friendly
                - If any limit is exceeded, shorten it before responding

                JSON format:
                [
                {
                    "id": "q01",
                    "title": "...",
                    "scenario": "...",
                    "code": "",
                    "question": "...",
                    "options": ["...", "...", "...", "..."],
                    "correct": "D",
                    "explanation": "..."
                }
                ]
                """,

    "command_output": """
                        You are a Senior {{subject}} (Linux) expert creating SHORT-FORM content for Instagram reels.

                        Generate {{n}} Linux command-output multiple-choice questions about {{topic}}.

                        STRICT RULES (must follow):
                        - Return ONLY valid JSON
                        - No text outside JSON
                        - Keep content concise and reel-friendly
                        - Do NOT exceed length limits below

                        Each question MUST contain:
                        - title: max 6 words
                        - code: shell command(s), max 4 lines, no sudo/destructive ops
                        - output: short expected output, max 3 lines, under 80 characters each
                        - question: exactly 1 sentence, under 120 characters
                        - options: exactly 4 items, each under 60 characters
                        - correct: one of "A", "B", "C", "D"
                        - explanation: max 2 short sentences, under 160 characters total

                        Additional constraints:
                        - Prefer portable POSIX commands (awk/sed/grep/coreutils)
                        - Avoid irreversible operations; keep examples safe/read-only
                        - If any limit is exceeded, shorten it before responding

                        JSON format:
                        [
                        {
                            "id": "q01",
                            "title": "...",
                            "code": "wc -l file.txt",
                            "output": "42",
                            "question": "...",
                            "options": ["...", "...", "...", "..."],
                            "correct": "B",
                            "explanation": "..."
                        }
                        ]
                        """,

    "qa": """
           You are a Senior {{subject}} (DevOps/SRE) expert creating SHORT-FORM content for Instagram reels.

           Generate {{n}} concise DevOps/SRE multiple-choice questions about {{topic}}.

           STRICT RULES (must follow):
           - Return ONLY valid JSON
           - No text outside JSON
           - Keep content concise and reel-friendly
           - Do NOT exceed length limits below

           Each question MUST contain:
           - title: max 7 words
           - code: either empty string ("") or a tiny snippet under 40 characters
           - question: exactly 1 sentence, under 180 characters
           - options: exactly 4 items, each under 70 characters
           - correct: one of "A", "B", "C", "D"
           - explanation: max 2 short sentences, under 200 characters total

           Additional constraints:
           - Favor practical, production-minded scenarios (alerts, rollbacks, scaling)
           - Keep the tone conversational, like a voiceover
           - If any limit is exceeded, shorten it before responding

           JSON format:
           [
           {
               "id": "q01",
               "title": "...",
               "code": "",
               "question": "...",
               "options": ["...", "...", "...", "..."],
               "correct": "A",
               "explanation": "..."
           }
           ]
           """
}





