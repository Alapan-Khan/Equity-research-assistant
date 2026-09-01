import sys
from graph.flow import build_graph
from graph.state import GraphState
from eval.eval_set import EVAL_SET


def run_eval():
    app = build_graph()
    results = []

    for i, case in enumerate(EVAL_SET):
        print(f"\n{'=' * 60}")
        print(f"[{i+1}/{len(EVAL_SET)}] {case['query']}")

        initial_state: GraphState = {
            "query": case["query"], "route": "", "retrieved_context": "",
            "is_relevant": False, "retry_count": 0,
            "final_answer": "", "sources": []
        }

        try:
            result = app.invoke(initial_state)
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"query": case["query"], "route_ok": False, "keywords_ok": False, "error": str(e)})
            continue

        actual_route = result.get("route", "")
        answer = result.get("final_answer", "")

        # Note: after a retry, 'route' in final state may have been rewritten as query text
        # changed but route field is preserved by our routing fix, so this checks the
        # ORIGINAL classification behavior correctly.
        route_ok = actual_route == case["expected_route"]

        keywords_ok = any(kw.lower() in answer.lower() for kw in case["expected_keywords"])

        status_route = "PASS" if route_ok else "FAIL"
        status_kw = "PASS" if keywords_ok else "FAIL"

        print(f"  Route:    {status_route}  (expected: {case['expected_route']}, got: {actual_route})")
        print(f"  Keywords: {status_kw}  (looking for: {case['expected_keywords']})")

        if not keywords_ok:
            print(f"  Answer preview: {answer[:200]}")

        results.append({
            "query": case["query"],
            "route_ok": route_ok,
            "keywords_ok": keywords_ok,
        })

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")

    route_passes = sum(1 for r in results if r["route_ok"])
    keyword_passes = sum(1 for r in results if r["keywords_ok"])
    total = len(results)

    print(f"Routing accuracy:  {route_passes}/{total} ({100*route_passes/total:.0f}%)")
    print(f"Answer accuracy:   {keyword_passes}/{total} ({100*keyword_passes/total:.0f}%)")

    for r in results:
        marks = f"route={'OK' if r['route_ok'] else 'X'} keywords={'OK' if r['keywords_ok'] else 'X'}"
        print(f"  [{marks}] {r['query']}")

    return results


if __name__ == "__main__":
    run_eval()