from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ContentSpec:
    subject: str
    content_type: str
    assets: List[str]
    topics: List[str]


CONTENT_REGISTRY: Dict[str, ContentSpec] = {
    "python": ContentSpec(
        subject="python",
        content_type="code_output",
        assets=["code", "explanation"],
        topics=[
            "Python internals and memory model",
            "List comprehensions and generators",
            "Variable scope and closures",
            "Mutability and immutability",
            "Decorators",
            "Async and await",
            "Threading and GIL",
            "Standard library gotchas",
            "Object-oriented Python internals",
            "Python truthiness and comparisons",
        ],
    ),

    "javascript": ContentSpec(
        subject="javascript",
        content_type="code_output",
        assets=["code", "explanation"],
        topics=[
            "Hoisting and temporal dead zone",
            "Closures and lexical scope",
            "this binding rules",
            "Async/await and promises",
            "Event loop and microtasks",
            "Prototype chain behaviors",
            "Array/Object mutation pitfalls",
        ],
    ),

    "rust": ContentSpec(
        subject="rust",
        content_type="code_output",
        assets=["code", "explanation"],
        topics=[
            "Ownership and borrowing basics",
            "Lifetimes in functions",
            "Traits and generics",
            "Pattern matching tricks",
            "Error handling with Result",
            "Smart pointers (Rc, Arc, RefCell)",
            "Concurrency with threads and channels",
        ],
    ),

    "golang": ContentSpec(
        subject="golang",
        content_type="code_output",
        assets=["code", "explanation"],
        topics=[
            "Slices vs arrays semantics",
            "Maps and zero values",
            "Goroutines and channels",
            "Select and timeouts",
            "Interfaces and method sets",
            "Defer execution order",
            "Context cancellation patterns",
        ],
    ),

    "sql": ContentSpec(
        subject="sql",
        content_type="query_output",
        assets=["query", "table"],
        topics=[
            "GROUP BY edge cases",
            "JOIN behavior with NULLs",
            "HAVING vs WHERE",
            "Window functions",
            "Subqueries vs CTEs",
        ],
    ),

    "regex": ContentSpec(
        subject="regex",
        content_type="pattern_match",
        assets=["input", "regex"],
        topics=[
            "Greedy vs lazy matching",
            "Lookahead and lookbehind",
            "Character classes",
            "Anchors and boundaries",
        ],
    ),

    "system_design": ContentSpec(
        subject="system_design",
        content_type="scenario",
        assets=["diagram", "text"],
        topics=[
            "Rate limiting",
            "Caching strategies",
            "Queue backpressure",
            "Database sharding",
        ],
    ),

    "linux": ContentSpec(
        subject="linux",
        content_type="command_output",
        assets=["terminal"],
        topics=[
            "wc / awk / sed",
            "Pipe behavior",
            "Exit codes",
            "Subshells",
        ],
    ),

    "docker_k8s": ContentSpec(
        subject="docker_k8s",
        content_type="qa",
        assets=["question", "explanation"],
        topics=[
            "OOMKilled",
            "Image layers",
            "Pod restarts",
            "ConfigMaps vs Secrets",
        ],
    ),
}
