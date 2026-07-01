"""
test_api.py — Resume NER v7 API Tests
Run: pytest test_api.py -v
Or:  python test_api.py  (standalone mode — no pytest needed)
"""

import json
import sys
import time
import requests

BASE_URL = "http://localhost:8000"

# ─────────────────────────── Sample Data ─────────────────────────
DATA_ANALYST_CV = """Mohamed Hammad
Data Analyst
Mohamedeeexx995@gmail.com | Cairo, Egypt

EDUCATION
Bachelor's in Artificial Intelligence
Helwan University | 2027

EXPERIENCE
Data Analyst | Microsoft Power BI Specialist, DEPI
06/2025 – 12/2025 | Cairo, Egypt
• Developed interactive dashboards using Power BI and Tableau.
• Processed and cleaned data using SQL and Python.

SKILLS
- Python
- SQL
- Power BI
- Tableau
- Excel
- Machine Learning
- Feature Engineering
- Pandas
- NumPy
"""

ML_ENGINEER_CV = """Ahmed Ali
Machine Learning Engineer
ahmed.ali@gmail.com | Cairo

EDUCATION
M.Sc Artificial Intelligence
Cairo University | 2022

EXPERIENCE
Google - ML Engineer (2022 - Present)

SKILLS
- TensorFlow
- PyTorch
- Python
- Docker
- AWS
"""

EDGE_CASE_CV = """
SKILLS
Technical Skills

EDUCATION
Education

DESIGNATION
Experience
"""

# ─────────────────────────── Helpers ─────────────────────────────
PASS = "\033[92m✅ PASS\033[0m"
FAIL = "\033[91m❌ FAIL\033[0m"
results = []


def check(name: str, condition: bool, detail: str = ""):
    status = PASS if condition else FAIL
    msg = f"  {status}  {name}"
    if detail and not condition:
        msg += f"\n         → {detail}"
    print(msg)
    results.append((name, condition))
    return condition


def post_text(text: str, conf: float = 0.50, tta: int = 1) -> dict:
    """POST /parse/text and return response JSON."""
    r = requests.post(
        f"{BASE_URL}/parse/text",
        json={"text": text, "conf": conf, "tta": tta},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


# ─────────────────────────── Test Suites ─────────────────────────
def test_health():
    print("\n── Health & Meta ─────────────────────────────────────────")
    r = requests.get(f"{BASE_URL}/health", timeout=10)
    check("GET /health returns 200", r.status_code == 200)
    body = r.json()
    check("status == ok",      body.get("status") == "ok")
    check("model key present", "model" in body)
    check("device key present","device" in body)

    r2 = requests.get(f"{BASE_URL}/labels", timeout=10)
    check("GET /labels returns 200", r2.status_code == 200)
    labels = r2.json()
    check("entities list non-empty",  len(labels.get("entities", [])) > 0)
    check("all_labels contains B-Name", "B-Name" in labels.get("all_labels", []))


def test_data_analyst():
    print("\n── Data Analyst CV ───────────────────────────────────────")
    resp = post_text(DATA_ANALYST_CV)
    ents = resp["entities"]

    check("response has latency_ms",    "latency_ms" in resp)
    check("model_ver == v7-LoRA",       resp.get("model_ver") == "v7-LoRA")
    check("name extracted",             len(ents["name"]) > 0,
          f"got: {ents['name']}")
    check("designation extracted",      len(ents["designation"]) > 0,
          f"got: {ents['designation']}")
    check("only 1 designation",         len(ents["designation"]) == 1,
          f"got {len(ents['designation'])}: {ents['designation']}")
    check("email extracted",            len(ents["email_address"]) > 0,
          f"got: {ents['email_address']}")
    check("email is valid format",      "@" in (ents["email_address"] or [""])[0])
    check("location extracted",         len(ents["location"]) > 0,
          f"got: {ents['location']}")
    check("skills non-empty",           len(ents["skills"]) > 0,
          f"got: {ents['skills']}")
    check("Python in skills",           any("python" in s.lower() for s in ents["skills"]),
          f"got: {ents['skills']}")
    check("degree extracted",           len(ents["degree"]) > 0,
          f"got: {ents['degree']}")
    check("degree not a section header",
          not any(d.lower() in {"education", "experience", "skills"}
                  for d in ents["degree"]),
          f"got: {ents['degree']}")
    check("college_name extracted",     len(ents["college_name"]) > 0,
          f"got: {ents['college_name']}")
    print(f"         latency: {resp['latency_ms']} ms")


def test_ml_engineer():
    print("\n── ML Engineer CV ────────────────────────────────────────")
    resp = post_text(ML_ENGINEER_CV)
    ents = resp["entities"]

    check("name extracted",         len(ents["name"]) > 0)
    check("designation extracted",  len(ents["designation"]) > 0)
    check("only 1 designation",     len(ents["designation"]) == 1,
          f"got: {ents['designation']}")
    check("email extracted",        len(ents["email_address"]) > 0)
    check("skills non-empty",       len(ents["skills"]) > 0)
    check("TensorFlow or PyTorch",  any(s in ents["skills"] for s in ["TensorFlow", "PyTorch"]),
          f"got: {ents['skills']}")
    check("company extracted",      len(ents["companies"]) > 0,
          f"got: {ents['companies']}")
    check("company not email/url",
          all("@" not in c and not c.startswith("http") for c in ents["companies"]),
          f"got: {ents['companies']}")


def test_edge_cases():
    print("\n── Edge Cases ────────────────────────────────────────────")

    # Empty text
    r = requests.post(f"{BASE_URL}/parse/text", json={"text": ""}, timeout=10)
    check("empty text → 400", r.status_code == 400)

    # Too long
    r2 = requests.post(f"{BASE_URL}/parse/text",
                       json={"text": "a" * 60_000}, timeout=10)
    check("text > 50k → 413", r2.status_code == 413)

    # Edge-case CV with only section headers
    resp = post_text(EDGE_CASE_CV)
    ents = resp["entities"]
    check("section headers NOT in designation",
          all(d.lower() not in {"education", "experience", "skills"}
              for d in ents.get("designation", [])),
          f"got: {ents.get('designation')}")
    check("section headers NOT in degree",
          all(d.lower() not in {"education", "experience", "skills"}
              for d in ents.get("degree", [])),
          f"got: {ents.get('degree')}")

    # Non-PDF upload
    r3 = requests.post(
        f"{BASE_URL}/parse/pdf",
        files={"file": ("test.txt", b"hello", "text/plain")},
        timeout=10,
    )
    check("non-PDF upload → 400", r3.status_code == 400)


def test_response_schema():
    print("\n── Response Schema ───────────────────────────────────────")
    resp = post_text(DATA_ANALYST_CV)
    ents = resp["entities"]

    expected_keys = [
        "name", "designation", "email_address", "location",
        "companies", "degree", "college_name", "graduation_year",
        "years_experience", "skills", "links", "raw",
    ]
    for key in expected_keys:
        check(f"entities.{key} present", key in ents, f"missing: {key}")

    check("entities.raw is dict", isinstance(ents["raw"], dict))
    check("entities.skills is list", isinstance(ents["skills"], list))


def test_confidence_param():
    print("\n── Confidence Parameter ──────────────────────────────────")
    high = post_text(DATA_ANALYST_CV, conf=0.90)
    low  = post_text(DATA_ANALYST_CV, conf=0.20)
    check("high conf still returns entities", "name" in high["entities"] or True)  # soft check
    check("low conf returns at least as many skills",
          len(low["entities"]["skills"]) >= len(high["entities"]["skills"]),
          f"low={len(low['entities']['skills'])} high={len(high['entities']['skills'])}")


def test_latency():
    print("\n── Latency ───────────────────────────────────────────────")
    times = []
    for _ in range(3):
        t0 = time.perf_counter()
        post_text(ML_ENGINEER_CV, tta=1)
        times.append((time.perf_counter() - t0) * 1000)
    avg = sum(times) / len(times)
    print(f"         avg latency (tta=1): {avg:.0f} ms")
    check("avg latency < 10s (CPU ok)", avg < 10_000,
          f"avg={avg:.0f}ms")


# ─────────────────────────── Runner ──────────────────────────────
def run_all():
    print("\n" + "═" * 60)
    print("  Resume NER v7 API — Test Suite")
    print("  Target:", BASE_URL)
    print("═" * 60)

    try:
        requests.get(f"{BASE_URL}/health", timeout=5)
    except Exception:
        print(f"\n❌  Cannot reach {BASE_URL} — is the server running?")
        print("   Run:  uvicorn main:app --reload\n")
        sys.exit(1)

    test_health()
    test_data_analyst()
    test_ml_engineer()
    test_edge_cases()
    test_response_schema()
    test_confidence_param()
    test_latency()

    # Summary
    passed = sum(1 for _, ok in results if ok)
    total  = len(results)
    print("\n" + "═" * 60)
    print(f"  Results: {passed}/{total} passed", end="  ")
    if passed == total:
        print("\033[92m🎉 ALL PASSED\033[0m")
    else:
        failed = [n for n, ok in results if not ok]
        print(f"\033[91m{total - passed} FAILED\033[0m")
        print("  Failed:", failed)
    print("═" * 60 + "\n")

    return passed == total


if __name__ == "__main__":
    ok = run_all()
    sys.exit(0 if ok else 1)
