"""Synthetic applicant generator. Sensitive attributes (gender, region) are generated
independently of merit so we can verify the pipeline does not introduce bias."""
import numpy as np
import pandas as pd

FEATURES = ["gpa", "gre", "toefl", "sop", "lor", "research", "univ_rating"]
REGIONS = ["South Asia", "East Asia", "Europe", "North America", "Africa", "Middle East", "Latin America"]
TOPICS = [
    "machine learning research on healthcare data", "distributed systems and cloud infrastructure",
    "building a startup in fintech", "computer vision for agriculture",
    "natural language processing for low-resource languages", "robotics and autonomous navigation",
    "cybersecurity and privacy engineering", "data engineering and analytics at scale",
]

def generate(n: int = 5000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "gpa": np.clip(rng.normal(3.3, 0.4, n), 2.0, 4.0).round(2),
        "gre": np.clip(rng.normal(315, 15, n), 260, 340).round(),
        "toefl": np.clip(rng.normal(100, 10, n), 60, 120).round(),
        "sop": np.clip(rng.normal(3.5, 0.9, n), 1, 5).round(1),
        "lor": np.clip(rng.normal(3.5, 0.9, n), 1, 5).round(1),
        "research": rng.integers(0, 2, n),
        "univ_rating": rng.integers(1, 6, n),
        "gender": rng.choice(["F", "M", "X"], n, p=[0.45, 0.52, 0.03]),
        "region": rng.choice(REGIONS, n),
        "topic": rng.choice(TOPICS, n),
    })
    z = (3.0 * (df.gpa - 3.3) + 0.06 * (df.gre - 315) + 0.02 * (df.toefl - 100)
         + 0.35 * (df.sop - 3.5) + 0.35 * (df.lor - 3.5) + 0.6 * df.research
         + 0.25 * (df.univ_rating - 3) - 0.2)
    df["admit"] = (rng.random(n) < 1 / (1 + np.exp(-z))).astype(int)
    return df

def make_essay(topic: str, rng=None) -> str:
    rng = rng or np.random.default_rng()
    parts = [
        f"My interest in {topic} began during my undergraduate years, when a course project showed me how much a small team can achieve with the right tools.",
        "I spent two summers working on practical problems, which taught me to debug patiently, communicate clearly with collaborators, and measure results honestly.",
        "One difficult moment came when our first approach failed completely; rather than giving up, we reviewed the data, found a labeling issue, and rebuilt the pipeline.",
        "I want to join your program because its faculty combine rigorous theory with real deployments, and I hope to contribute to a research group while learning from them.",
        "After graduation I plan to build systems that are reliable, fair and useful to people outside the lab.",
    ]
    k = int(rng.integers(3, 6))
    return " ".join(parts[:k])
