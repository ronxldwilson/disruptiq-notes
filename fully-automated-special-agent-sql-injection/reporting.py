
import json, time
from pathlib import Path

def save_report(data):
    Path("results").mkdir(exist_ok=True)
    filename = f"results/report_{int(time.time())}.json"
    with open(filename, "w") as fw:
        json.dump(data, fw, indent=2)
    return filename
