#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.orchestrator import Orchestrator

if __name__ == "__main__":
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run_analysis())
