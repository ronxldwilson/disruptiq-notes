
from agents import code_analysis, payload_generator, fuzzing, response_analysis, reporting

def main():
    # 1. Extract endpoints
    endpoints = code_analysis.analyze_codebase("./app")

    # 2. Generate payloads
    for ep in endpoints:
        ep["payloads"] = []
        for param in ep.get("params", []):
            ep["payloads"].extend(payload_generator.generate_payloads(param))

    # 3. Fuzz endpoints
    results = fuzzing.fuzz_all(endpoints)

    # 4. Analyze responses
    for ep_result in results:
        for r in ep_result:
            r["error_detected"], r["error_pattern"] = response_analysis.analyze_response(r["text_excerpt"])

    # 5. Save report
    filename = reporting.save_report({
        "base_url": "http://localhost:5000",
        "timestamp": int(time.time()),
        "results": results
    })
    print("Report saved to:", filename)

if __name__ == "__main__":
    main()
