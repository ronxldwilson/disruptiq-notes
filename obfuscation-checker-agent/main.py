#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import main

if __name__ == "__main__":
    asyncio.run(main())
