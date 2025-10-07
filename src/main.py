# src/main.py
"""
CLI entrypoint to run a query against the Google-only RAG system.
Usage:
python src/main.py --query "What percentage of Google's 2023 revenue came from advertising?"
"""

import argparse
from src.agent import synthesize
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, required=True, help="Financial question about Google")
    args = parser.parse_args()
    result = synthesize(args.query)
    print(json.dumps(result, indent=2))
