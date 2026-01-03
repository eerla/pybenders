# Content length limits per subject (characters)
# Optimized for mobile reel readability with current font sizes
CONTENT_LIMITS = {
    "python": {
        "scenario": 250,
        "question": 200,
        "explanation": 300,
    },
    "javascript": {
        "scenario": 250,
        "question": 200,
        "explanation": 300,
    },
    "rust": {
        "scenario": 250,
        "question": 200,
        "explanation": 300,
    },
    "golang": {
        "scenario": 250,
        "question": 200,
        "explanation": 300,
    },
    "sql": {
        "scenario": 250,
        "question": 200,
        "explanation": 300,
    },
    "regex": {
        "scenario": 250,
        "question": 200,
        "explanation": 300,
    },
    "linux": {
        "scenario": 250,
        "question": 200,
        "explanation": 300,
    },
    "system_design": {
        "scenario": 350,      # More context for architectural decisions
        "question": 150,      # Questions are usually concise once context is set
        "explanation": 400,   # Detailed reasoning for design trade-offs
    },
    "docker_k8s": {
        "scenario": 350,      # More context for cluster/deployment scenarios
        "question": 150,      # Questions are usually concise
        "explanation": 400,   # Detailed reasoning for troubleshooting/decisions
    },
    "mind_benders": {
        "puzzle": 100,        # Main puzzle text
        "question": 100,      # The question asked
        "explanation": 300,   # Fun explanation of the answer
        "fun_fact": 200,      # Optional trivia/fun fact
    },
}

PROMPT_TEMPLATES = {
    "code_output": """
                    You are a Senior {{subject}} expert creating SHORT-FORM content for Instagram reels.

                    Generate {{n}} DIFFERENT and VARIED tricky {{subject}} multiple-choice questions about {{topic}}.

                    STRICT RULES (must follow):
                    - Return ONLY valid JSON
                    - No text outside JSON
                    - Keep content concise and reel-friendly
                    - Do NOT exceed length limits below
                    - Make each of the {{n}} questions noticeably unique in scenario, code style, or trick angle
                    - Avoid repeating the same pattern, variable usage, or example structure across questions
                                        - Use proper JSON escaping in all string fields:
                                            - Escape inner double quotes as \\\"\"\\\"
                                            - Escape backslashes as \\\\ (e.g., r"\\\\d" if present)
                                            - Use literal \\n for newlines (never actual line breaks in JSON)

                    Each question MUST contain:
                    - title: max 8 words
                    - code: max 12 lines, no comments, no blank lines; use \\n for newlines and escape quotes as \\\"\"\\\" and backslashes as \\\\ in JSON
                    - question: exactly 1 sentence
                    - options: exactly 4 items, each under 60 characters
                    - correct: one of "A", "B", "C", "D"
                    - explanation: max 2-3 short sentences, under 300 characters total

                    Additional constraints:
                    - Avoid long variable names
                    - Avoid nested examples or edge-case-heavy code
                    - Prefer clarity over completeness
                    - Assume viewer has intermediate {{subject}} knowledge
                    - Vary the context or twist: use different real-world scenarios, error symptoms, or subtle variations of the concept
                    - Before responding, think: "Are these {{n}} questions clearly different from each other and from common tutorial examples?"
                    - If they feel too similar, rework one or more for freshness
                    - Code must fit within a single screen on a mobile device
                    - Explanation should sound like a spoken voiceover, not documentation
                    - Before final output, double-check every field obeys length limits and JSON escaping (\\" quotes, \\\\ backslashes, \\n newlines). Shorten if needed.

                    JSON format (note the \\n newlines and \\\" escaped quotes in code):
                    [
                    {
                        "id": "q01",
                        "title": "...",
                        "code": "fn main() {\\n    let v = vec![1, 2, 3];\\n    println!(\\\"{:?}\\\", v);\\n}",
                        "question": "...",
                        "options": ["...", "...", "...", "..."],
                        "correct": "B",
                        "explanation": "..."
                    }
                    ]
                    """,

    "query_output": """
                    You are a Senior {{subject}} (SQL) expert creating SHORT-FORM content for Instagram reels.

                    Generate {{n}} DIFFERENT and VARIED bite-sized SQL multiple-choice questions about {{topic}}.

                    STRICT RULES (must follow):
                    - Return ONLY valid JSON
                    - No text outside JSON
                    - CRITICAL JSON ESCAPING: In the "code" field, multi-line SQL MUST use \\n escape sequences
                      -- NEVER use backslash line continuations (\\) at end of lines
                      -- ALWAYS use literal \\n characters for newlines within the JSON string
                      -- Example: "WITH t AS (\\n  VALUES (1)\\n)\\nSELECT * FROM t;"
                    - Keep content concise and reel-friendly
                    - Everything must fit cleanly on a standard mobile phone screen (vertical reel)
                    - Do NOT exceed length limits below
                    - Make each of the {{n}} questions unique in logic, filter, aggregate, join, or NULL behavior
                    - ALWAYS embed up to 3–4 sample rows (and 3–4 columns) inline using a compact CTE (WITH + VALUES) inside "code" if needed to illustrate the logic
                    - NEVER ask vague "What is the output?" questions
                    - ALWAYS ask SPECIFIC, TESTABLE questions with ONE correct answer
                    - Options MUST include exactly 1 correct answer and 3 plausible-but-wrong answers derived from the shown sample data

                    CRITICAL: Question must be SPECIFIC and UNAMBIGUOUS. Choose ONE type:
                    1. COUNT questions: "How many rows does this return?" → options: [0, 1, 2, 3]
                    2. AGGREGATE questions: "What is the total/max/min/avg?" → options: specific numbers
                    3. SPECIFIC VALUE questions: "What value does this return for [specific row/condition]?" → options: specific values
                    4. FIRST/LAST questions: "What is the first row returned?" → options: specific row values
                    5. EXISTS/NULL questions: "Does this return NULL?" or "How many NULLs appear?" → options: Yes/No or counts
                    6. BEHAVIOR questions: "What happens when [specific condition]?" → options: specific outcomes

                    FORBIDDEN question types:
                    - "What is the output of the final SELECT?" (TOO VAGUE)
                    - "What does the query return?" (TOO VAGUE)
                    - Any question where multiple options could be partially correct

                    Each question MUST contain:
                    - title: max 8 words, describe the SQL concept being tested
                    - code: one compact SQL snippet:
                      -- single CTE with inline sample data via VALUES
                      -- final SELECT performing the logic under test
                      -- under 12 lines total; use \\n for line breaks (NOT backslash continuations), 2-space indentation
                    - question: exactly 1 sentence, under 110 characters, asking ONE SPECIFIC testable thing
                    - options: exactly 4 items (only ONE correct), each under 60 characters
                      -- Options must directly answer the specific question asked
                      -- If asking for count, show numbers; if asking for value, show values; if asking about behavior, show outcomes
                    - correct: one of "A", "B", "C", "D"
                    - explanation: max 2-3 short sentences, under 300 characters total, explaining WHY this specific result occurs with step-by-step logic

                    Additional constraints:
                    - Use short, clear column names (e.g., id, name, amount, status)
                    - Keep data realistic and minimal—focus on logic, not volume
                    - Wrong options should be plausible mistakes (off-by-one, wrong aggregate, misread LIKE, NULL misinterpretation)
                    - Verify internally that exactly ONE option matches the result of the final SELECT using the provided sample data
                    - BEFORE finalizing: Execute the query mentally with the sample data to ensure the correct answer is actually correct
                    - If more than one option could be correct, adjust the sample data or make the question more specific
                    - Explanation must sound natural and spoken (like reel voiceover)

                    GOOD EXAMPLES of specific questions:
                    - "How many rows have amount > 100?"
                    - "What is the maximum price?"
                    - "What value appears for the row where id = 2?"
                    - "How many NULL values are in the result?"
                    - "What is the first name returned when ordered by date?"

                    BAD EXAMPLES (never use these):
                    - "What is the output of the final SELECT?" (which row? all rows? what aspect?)
                    - "What does the query return?" (too vague)

                    JSON format:
                    [
                    {
                        "id": "q01",
                        "title": "LIKE Pattern Edge Case",
                        "code": "WITH t(id, name) AS (\\n  VALUES (1,'Alice'), (2,'Mark'), (3,'Sara'), (4,'James')\\n)\\nSELECT COUNT(*)\\nFROM t\\nWHERE name LIKE '%a%a%';",
                        "question": "How many rows match the pattern?",
                        "options": ["0", "1", "2", "3"],
                        "correct": "B",
                        "explanation": "Only 'Sara' contains two 'a' letters; the count is 1."
                    }
                    ]
                    """,

    "pattern_match": """
                    You are a Senior {{subject}} (regex) expert creating SHORT-FORM content for Instagram reels.

                    Generate EXACTLY {{n}} DIFFERENT and VARIED regex pattern-matching multiple-choice questions about {{topic}}.

                    STRICT RULES (must follow):
                    - Return ONLY valid JSON
                    - No text outside JSON
                    - Generate EXACTLY {{n}} questions, no more, no less
                    - Keep content concise and reel-friendly
                    - Everything must fit cleanly on a standard mobile phone screen (vertical reel)
                    - Do NOT exceed length limits below
                    - Make each of the {{n}} questions unique in pattern, operation, test string, or concept angle
                    - Avoid repeating similar patterns or gotchas across questions
                    - ALWAYS ask "What does this return?" or "What gets matched/captured/replaced?" - NEVER ask "which pattern is correct"
                    - The pattern and input are already in the code - focus on understanding the OUTPUT
                    - CRITICAL JSON ESCAPING: In the code field, ALWAYS escape backslashes as \\\\ (four backslashes in JSON become one in the pattern)
                        - Write \\\\d, \\\\w, \\\\s, \\\\b, \\\\B, \\\\( etc. in JSON code strings
                        - This applies EVEN when the code uses r'...' raw strings
                        - Example: "code": "re.findall(r'(\\\\d{3})-(\\\\d{3})', '123-456')"
                        
                    Each question MUST contain:
                    - title: max 6 words
                    - code: Complete Python code showing pattern + input + operation (1-3 lines, total under 120 chars)
                    - CRITICAL: Escape ALL backslashes in JSON as \\\\ - do NOT use single backslash \\d, use \\\\d
                    - question: Ask about the OUTPUT/RESULT, exactly 1 sentence, under 155 characters
                    - options: exactly 4 items showing possible outputs, each under 60 characters
                    - correct: one of "A", "B", "C", "D"
                    - explanation: max 2-3 short sentences explaining WHY the pattern behaves this way, under 300 characters total

                    Question formats to rotate through:
                    1. "What does this return?" - for findall, search, match results
                    2. "What gets captured by group(1)?" - for capture groups
                    3. "What's the output?" - for sub replacements
                    4. "How many matches?" - for findall with counting
                    5. "Which text gets matched?" - for specific match behavior

                    Code variety (rotate through different operations):
                    - re.findall(r'pattern', 'test string')
                    - re.search(r'pattern', 'test').group()
                    - re.sub(r'pattern', 'replacement', 'text')
                    - re.match(r'pattern', 'test string')
                    - re.split(r'pattern', 'test string')
                    - m = re.search(r'(group)', 'text'); m.group(1)

                    Additional constraints:
                    - Pattern under 40 characters, test string under 80 characters
                    - Avoid exotic backreferences that hurt readability
                    - Use lookarounds only when demonstrating the specific topic feature
                    - Vary contexts: emails, logs, filenames, URLs, phone numbers, code snippets, dates, etc.
                    - Options should be realistic outputs (lists, strings, None, numbers) not vague descriptions
                    - Before output, verify all fields fit mobile screen and feel distinctly different
                    - Explanation must sound natural and spoken—like reel voiceover
                    - If any limit is exceeded, shorten it before responding

                    JSON format example (CRITICAL: note the \\\\ for backslashes):
                    [
                    {
                        "id": "q01",
                        "title": "Capturing vs Non-Capturing Groups",
                        "code": "import re\\nre.findall(r'(?:\\\\d{3})-(\\\\d{3})', '123-456 789-012')",
                        "question": "What does this return?",
                        "options": ["['456', '012']", "['123', '789']", "['456']", "[]"],
                        "correct": "A",
                        "explanation": "The (?:\\\\d{3}) non-capturing group matches but doesn't capture. findall returns only group(1), the captured digits."
                    }
                    ]

                    DO NOT copy this example - create completely new questions about {{topic}}.
                    Generate EXACTLY {{n}} questions.
                    """,
                    
    "scenario": """
                You are a Senior {{subject}} (system design) expert creating SHORT-FORM content for Instagram reels.

                Generate {{n}} DIFFERENT and VARIED lightweight system design scenarios about {{topic}}.

                STRICT RULES (must follow):
                - Return ONLY valid JSON
                - No text outside JSON
                - Keep content concise and reel-friendly
                - Everything must fit cleanly on a standard mobile phone screen
                - Do NOT exceed length limits below
                - Make each of the {{n}} questions unique in application context, workload type, or trade-off focus
                - Avoid repeating similar services, data patterns, or classic examples

                Each question MUST contain:
                - title: max 8 words
                - scenario: concise but COMPLETE setup with key requirements, scale, and workload (under 350 chars). This is the hook — it MUST provide enough context to answer the question correctly without external knowledge.
                - code: ""  (always empty — no code or snippets needed)
                - question: exactly 1 sentence, under 150 characters (keep it focused and concise)
                - options: exactly 4 items, each under 75 characters
                - correct: one of "A", "B", "C", "D"
                - explanation: 2-3 short confident sentences, like reel voiceover (under 400 chars total - use this space to explain WHY with trade-offs)

                Additional constraints:
                - Focus on practical real-world trade-offs, not theoretical designs
                - Always highlight real-world trade-offs: scalability, consistency, latency, availability, cost, complexity
                - Use diverse contexts: social feeds, messaging, e-commerce, analytics, gaming, IoT, etc.
                - Vary scale and constraints: high reads vs writes, global vs regional, spiky vs steady traffic
                - Keep it lightweight — no diagrams or deep math, just sharp insight
                - Before output, verify all fields are mobile-friendly and questions feel distinctly fresh
                - If anything feels repetitive or too long, rework for variety and brevity
                - Explanation must sound confident and spoken, like a quick reel voiceover
                - No code snippets, no diagrams — pure scenario + decision
                
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

                    Generate {{n}} DIFFERENT and VARIED Linux command-output multiple-choice questions about {{topic}}.

                    STRICT RULES (must follow):
                    - Return ONLY valid JSON
                    - No text outside JSON
                    - Keep content concise and reel-friendly
                    - Everything must fit cleanly on a standard mobile phone screen
                    - Do NOT exceed length limits below
                    - Make each of the {{n}} questions unique in command style, input data, or trick angle
                    - Avoid repeating similar commands or patterns

                    Each question MUST contain:
                    - title: max 6 words
                    - code: shell command(s), max 6 lines, no sudo/destructive ops
                    - output: short expected output, max 3 lines, under 80 characters each
                    - question: exactly 1 sentence, under 120 characters
                    - options: exactly 4 items, each under 55 characters
                    - correct: one of "A", "B", "C", "D"
                    - explanation: max 2-3 short sentences explaining command behavior, under 300 characters total

                    Additional constraints:
                    - If the {{topic}} starts with "What does" followed by a common Linux command (e.g., "What does grep do?", "What does ls do?"), generate a command-purpose quiz: show the plain command (or simple safe usage), ask what it primarily does, with one correct description and three plausible but incorrect ones.
                    - Commands must be self-contained — NEVER assume unseen files or prior state
                    - Always use here-strings (<<<), here-docs (<<EOF), or inline data when input is needed
                    - Preferred patterns: echo "data" | cmd, cmd <<< "input", cat <<EOF ... EOF
                    - If a file is used, create it inline first (e.g., cat >file <<< "content"; cmd file)
                    - Prefer portable POSIX commands (grep, awk, sed, cut, sort, uniq, wc, etc.)
                    - Avoid irreversible, dangerous, or environment-dependent operations
                    - Vary input data: logs, lists, tables, paths, process output, etc.
                    - Before output, verify: "Can a viewer understand the output without any prior context?"
                    - If anything feels unclear or assumes hidden state, rework it to be fully self-contained
                    - Explanation must sound natural and spoken, like a quick reel voiceover

                    JSON format:
                    [
                    {
                        "id": "q01",
                        "title": "...",
                        "code": "echo \"hello\\nworld\\nhello\" | sort | uniq -c",
                        "output": "      2 hello\\n      1 world",
                        "question": "...",
                        "options": ["...", "...", "...", "..."],
                        "correct": "B",
                        "explanation": "..."
                    }
                    ]
                    """,

    "qa": """
        You are a Senior {{subject}} (DevOps/SRE) expert creating SHORT-FORM content for Instagram reels.

        Generate {{n}} DIFFERENT and VARIED concise DevOps/SRE multiple-choice questions about {{topic}}.

        STRICT RULES (must follow):
        - Return ONLY valid JSON
        - No text outside JSON
        - Keep content concise and mobile reel-friendly
        - Everything must fit cleanly on a standard mobile phone screen
        - Do NOT exceed length limits below
        - Make each of the {{n}} questions unique in scenario, failure mode, or trade-off angle
        - Avoid repeating similar services, tools, or classic textbook examples

        Each question MUST contain:
        - title: max 7 words
        - scenario: concise but COMPLETE context (e.g., config snippet, symptoms, cluster state). Under 350 characters. This is essential — the question must be answerable from this alone.
        - code: short relevant snippet (under 50 chars) OR "" if not needed
        - question: exactly 1 sentence, under 150 characters. Must reference the scenario (e.g., "In this case,", "Given this config,", "What should you do when...")
        - options: exactly 4 items, each under 75 characters
        - correct: one of "A", "B", "C", "D"
        - explanation: 2-3 short confident sentences, like reel voiceover (under 400 chars total - use this space to explain WHY with troubleshooting insights)

        Additional constraints:
        - If the {{topic}} starts with "What does" or "What is", generate a definition/purpose quiz: ask what the command, status, or resource primarily does, with one correct description and three plausible but incorrect alternatives.
        - Focus on real-world production scenarios: scaling, rollouts, alerts, incidents, observability, recovery
        - Use diverse contexts: web apps, microservices, databases, CI/CD, batch jobs, multi-region, etc.
        - Vary failure types: OOM, crashes, network partitions, config errors, node loss, traffic spikes, image pull failures, node pressure, taints, affinity issues, etc.
        - Prefer practical over theoretical — highlight trade-offs, gotchas, and debugging insights
        - Before output, verify questions are mobile-friendly and feel distinctly different
        - If anything feels repetitive or too generic, rework for freshness and specificity
        - Explanation must sound confident, conversational, and spoken — perfect for reel voiceover - practical and insightful
        - When {{topic}} suggests definition (e.g., "What is a PodDisruptionBudget"), you may keep scenario very short or use it for purpose clarification
        
        JSON format:
        [
        {
            "id": "q01",
            "title": "...",
            "scenario": "...",
            "code": "",
            "question": "...",
            "options": ["...", "...", "...", "..."],
            "correct": "A",
            "explanation": "..."
        }
        ]
        """,
    "puzzle": """
            You are a creative puzzle master creating ENGAGING brain teasers for Instagram reels.

            Generate {{n}} DIFFERENT and VARIED mind-bending puzzles about {{topic}}.

            STRICT RULES:
            - Return ONLY valid JSON, nothing else
            - NO markdown code blocks (do NOT wrap in ```json ... ```)
            - NO text before or after the JSON
            - Use emojis when appropriate (🧠 🤔 ✅ ❌ 🎯 🔥)
            - Make each puzzle visually interesting
            - Vary difficulty and approach
            - Ensure answer is unambiguous

            Each puzzle MUST contain:
            - title: catchy name, max 5 words (e.g., "The Missing Number Mystery")
            - category: MUST be ONE of these EXACT values ONLY:
              "number_pattern", "logic", "math_trick", "word_puzzle", "visual", "trick_question", "age_puzzle", "time_puzzle", "probability", "aptitude", "reasoning"
              Choose the category that BEST fits the puzzle type. For example:
              - "number_pattern" for sequence puzzles (2, 6, 12, 20, ?)
              - "logic" for riddles and deductive reasoning
              - "math_trick" for mathematical patterns or number tricks
              - "word_puzzle" for word patterns (J, F, M, A, M = Jan, Feb, Mar, Apr, May)
              - "visual" for visual pattern puzzles with symbols/emojis
              - "trick_question" for questions with unexpected/tricky answers
              - "age_puzzle" for age relationship problems
              - "time_puzzle" for clock/time-based problems
              - "probability" for probability/chance questions
              - "aptitude" for general aptitude/IQ type questions
              - "reasoning" for abstract reasoning puzzles
            - puzzle: the main puzzle text, under 200 chars (use emojis where helpful)
            - visual_elements: optional symbols/emojis for visual puzzles (e.g., "▲ ▲ ○ = ?")
            - hint: optional subtle hint, max 80 chars (or empty string)
            - question: clear question, max 100 chars
            - options: exactly 4 items, each under 40 characters
            - correct: one of "A", "B", "C", "D"
            - explanation: fun, conversational explanation (like talking to a friend), under 250 chars
            - fun_fact: optional related trivia, under 150 chars (or empty string)

            Puzzle variety (rotate through):
            1. Number sequences: 2, 6, 12, 20, ? → category: "number_pattern"
            2. Logic riddles: "A bat and ball cost $1.10..." → category: "logic"
            3. Visual patterns: ▲ + ▲ = 10, ▲ + ○ = 7, ○ + ○ = ? → category: "visual"
            4. Math tricks: "Think of a number, multiply by 3..." → category: "math_trick"
            5. Word puzzles: J, F, M, A, M, ? (months) → category: "word_puzzle"
            6. Trick questions: "How many months have 28 days?" → category: "trick_question"
            7. Age puzzles: father/son age relationships → category: "age_puzzle"
            8. Time puzzles: clock hand angles → category: "time_puzzle"

            Additional constraints:
            - Make puzzles feel fresh and engaging (not textbook-ish)
            - Use everyday relatable contexts
            - Keep math simple (no complex calculations)
            - Explanations should be "aha!" moments, not academic
            - Before output, verify each puzzle is distinctly different
            - Emojis make it fun - use them naturally!
            - CRITICAL: Double-check category field matches one of the 11 valid categories above

            JSON format:
            [
            {
                "id": "q01",
                "title": "The Tricky Sequence",
                "category": "number_pattern",
                "puzzle": "2, 6, 12, 20, ?",
                "visual_elements": "",
                "hint": "Look at differences between numbers",
                "question": "What comes next?",
                "options": ["30", "28", "24", "32"],
                "correct": "A",
                "explanation": "The pattern is n² + n! So: 1²+1=2, 2²+2=6, 3²+3=12, 4²+4=20, 5²+5=30 🎯",
                "fun_fact": "This sequence appears in computer science as node connections in graphs!"
            }
            ]

            Generate EXACTLY {{n}} unique puzzles about {{topic}}.

        """,
}





