# Corrected Python file content and a runnable test.
import re
from pprint import pprint

def parse_express_routes(file_content):
    """
    Parse simple Express `app.METHOD('path', ...)` or `app.METHOD("path", ...)` occurrences.

    - Matches common HTTP methods (get, post, put, delete, patch, options, head, all).
    - Accepts either single or double quotes and requires the same quote to close the path.
    - Handles optional whitespace and either a comma after the path (when there are more args)
      or a closing parenthesis immediately (when arguments may be on following lines).
    - Aggregates methods for identical paths.
    """
    endpoints_map = {}
    # Use a robust regex: capture the method, the quote type, and the path (non-greedy).
    # \2 is a backreference to the opening quote, ensuring matching quote types.
    route_pattern = re.compile(
        r"""app\.(get|post|put|delete|patch|options|head|all)    # method
            \s*                                               # optional whitespace
            \(\s*                                             # opening parenthesis
            (['\"])                                           # capture the opening quote (single or double)
            (.*?)                                             # non-greedy capture of path
            \2                                                # matching closing quote (same as opening)
            \s*(?:,|\))                                        # either comma (more args) or immediate closing parenthesis
        """,
        re.IGNORECASE | re.VERBOSE | re.DOTALL,
    )

    for match in route_pattern.finditer(file_content):
        method = match.group(1).upper()
        path = match.group(3)
        endpoints_map.setdefault(path, set()).add(method)

    # Convert to list of dicts sorted by path for stable output
    endpoints = [{"path": path, "methods": sorted(list(methods))} for path, methods in sorted(endpoints_map.items())]
    return endpoints


# ---------- Example / test ----------
if __name__ == "__main__":
    file_content = """
    const express = require('express');
    const app = express();

    app.get('/api/data', (req, res) => {
      res.send('Hello from Node.js!');
    });

    app.post("/api/users", (req, res) => {
      res.send('Create a new user');
    });

    // variations
    app.put( '/api/data',function(req,res){ res.send('update'); });
    app.delete("/api/users") // no explicit callback shown on same line
    app.patch('/api/data' ,   (req, res) => {} );
    app.all("/catchall", (req,res)=>{});

    // a false positive example we should NOT match (router.*)
    router.get('/ignored', () => {});

    // template literals — intentionally ignored by this simple parser:
    app.get(`/templates/${id}`, () => {});
    """

    print("Detected endpoints:")
    pprint(parse_express_routes(file_content))
