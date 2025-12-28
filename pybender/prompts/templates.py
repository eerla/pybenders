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
                    - Vary the context or twist: use different real-world scenarios, error symptoms, or subtle variations of the concept
                    - Before responding, think: "Are these {{n}} questions clearly different from each other and from common tutorial examples?"
                    - If they feel too similar, rework one or more for freshness
                    - Code must fit within a single screen on a mobile device
                    - Explanation should sound like a spoken voiceover, not documentation
                    - Before final output, double-check every field obeys length limits. Shorten if needed.

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

                    Generate {{n}} DIFFERENT and VARIED bite-sized SQL multiple-choice questions about {{topic}}.

                    STRICT RULES (must follow):
                    - Return ONLY valid JSON
                    - No text outside JSON
                    - Keep content concise and reel-friendly
                    - Everything must fit cleanly on a standard mobile phone screen (vertical reel)
                    - Do NOT exceed length limits below
                    - Make each of the {{n}} questions unique in schema, trick angle, or query style
                    - Avoid repeating similar table structures, join patterns, or gotchas

                    Each question MUST contain:
                    - title: max 8 words
                    - schema: concise table definitions (<= 3 tables, <= 120 chars total)
                    - query: max 6 lines, no comments, no blank lines, no long CTEs
                    - code: exact copy of query (for rendering)
                    - question: exactly 1 sentence, under 110 characters
                    - options: exactly 4 items, each under 60 characters
                    - correct: one of "A", "B", "C", "D"
                    - explanation: max 2 short sentences, under 170 characters total

                    Additional constraints:
                    - Prefer portable ANSI SQL; avoid dialect-specific syntax
                    - Use short, clear table/column names (e.g., users, orders, id, name)
                    - Keep data realistic and minimal — focus on logic, not volume
                    - Vary scenarios: different domains (sales, logs, employees, etc.), join types, NULL behaviors, aggregates, etc.
                    - Before output, verify all fields fit mobile screen and are distinctly different
                    - If anything feels repetitive or too long, rework it for freshness and brevity
                    - Explanation must sound natural and spoken (like reel voiceover)

                    JSON format:
                    [
                    {
                        "id": "q01",
                        "title": "...",
                        "schema": "...",
                        "query": "...",
                        "code": "...",
                        "question": "...",
                        "options": ["...", "...", "...", "..."],
                        "correct": "C",
                        "explanation": "..."
                    }
                    ]
                    """,

    "pattern_match": """
                    You are a Senior {{subject}} (regex) expert creating SHORT-FORM content for Instagram reels.

                    Generate {{n}} DIFFERENT and VARIED regex pattern-matching multiple-choice questions about {{topic}}.

                    STRICT RULES (must follow):
                    - Return ONLY valid JSON
                    - No text outside JSON
                    - Keep content concise and reel-friendly
                    - Everything must fit cleanly on a standard mobile phone screen (vertical reel)
                    - Do NOT exceed length limits below
                    - Make each of the {{n}} questions unique in pattern, operation, test string, or concept angle
                    - Avoid repeating similar patterns or gotchas across questions
                    - ALWAYS ask "What does this return?" or "What gets matched/captured/replaced?" - NEVER ask "which pattern is correct"
                    - The pattern and input are already in the code - focus on understanding the OUTPUT

                    Each question MUST contain:
                    - title: max 6 words
                    - code: Complete Python code showing pattern + input + operation (1-3 lines, total under 120 chars)
                    - question: Ask about the OUTPUT/RESULT, exactly 1 sentence, under 155 characters
                    - options: exactly 4 items showing possible outputs, each under 60 characters
                    - correct: one of "A", "B", "C", "D"
                    - explanation: max 2 short sentences explaining WHY, under 155 characters total

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

                    JSON format examples (rotate through these styles):
                    [
                    {
                        "id": "q01",
                        "title": "Greedy vs Lazy Quantifier",
                        "code": "import re\\nre.findall(r'<.*?>', '<a><b><c>')",
                        "question": "What does this return?",
                        "options": ["['<a>', '<b>', '<c>']", "['<a><b><c>']", "['a', 'b', 'c']", "[]"],
                        "correct": "A",
                        "explanation": "The lazy quantifier .*? stops at first >, capturing each tag separately instead of everything."
                    },
                    {
                        "id": "q02",
                        "title": "Named Capture Group",
                        "code": "import re\\nm = re.search(r'(?P<user>\\\\w+)@(?P<dom>\\\\w+)', 'bob@site')\\nm.group('dom')",
                        "question": "What does this return?",
                        "options": ["'site'", "'bob'", "'bob@site'", "Error"],
                        "correct": "A",
                        "explanation": "Named groups extract parts by name. 'dom' captures text after @, giving us the domain."
                    },
                    {
                        "id": "q03",
                        "title": "Backreference Swap",
                        "code": "import re\\nre.sub(r'(\\\\w+)@(\\\\w+)', r'\\\\2.\\\\1', 'alice@example')",
                        "question": "What does this return?",
                        "options": ["'example.alice'", "'alice.example'", "'alice@example'", "'\\\\2.\\\\1'"],
                        "correct": "A",
                        "explanation": "\\\\2 is domain (second group), \\\\1 is user (first). sub() swaps their order with a dot."
                    }
                    ]

                    DO NOT copy these examples - create completely new questions about {{topic}}.
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
                - scenario: concise but COMPLETE setup with key requirements, scale, and workload (under 120 chars). This is the hook — it MUST provide enough context to answer the question correctly without external knowledge.                - code: ""  (always empty — no code or snippets needed)
                - question: exactly 1 sentence, under 280 characters  # Big increase — now the star
                - code: "" (always empty)
                - options: exactly 4 items, each under 75 characters
                - correct: one of "A", "B", "C", "D"
                - explanation: 1-2 short confident sentences, like reel voiceover (under 210 chars total)

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
                    - code: shell command(s), max 4 lines, no sudo/destructive ops
                    - output: short expected output, max 3 lines, under 80 characters each
                    - question: exactly 1 sentence, under 120 characters
                    - options: exactly 4 items, each under 55 characters
                    - correct: one of "A", "B", "C", "D"
                    - explanation: max 2 short sentences, under 155 characters total

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
        - scenario: concise but COMPLETE context (e.g., config snippet, symptoms, cluster state). Under 120 characters. This is essential — the question must be answerable from this alone.
        - code: short relevant snippet (under 50 chars) OR "" if not needed
        - question: exactly 1 sentence, under 280 characters. Must reference the scenario (e.g., "In this case,", "Given this config,", "What should you do when...")
        - options: exactly 4 items, each under 75 characters
        - correct: one of "A", "B", "C", "D"
        - explanation: 1-2 short confident sentences, like reel voiceover (under 210 chars total)

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
        """
}





