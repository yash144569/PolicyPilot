"""
PolicyPilot Regression Test Suite
==================================
Run this after ANY change to ingestion.py / query.py / api.py / the prompt,
or after uploading a new PDF, to make sure nothing that was already fixed
got silently broken again.

Usage:
    1. Make sure the FastAPI server is running (uvicorn api:app --reload)
    2. Make sure the correct PDF is uploaded (health policy for most tests
       below; the motor-policy tests are marked separately)
    3. Run:  python3 test_policypilot.py
    4. Read the PASS/FAIL summary at the bottom

Each test case has:
    - question:            what to ask
    - must_contain:        substrings that MUST appear in the answer (case-insensitive)
    - must_not_contain:    substrings that must NOT appear (catches known past bugs)

This is intentionally simple (substring matching, not exact-match) because
LLM phrasing varies run-to-run — we're checking for the FACTS being right,
not exact wording.
"""

import requests
import sys

API_URL = "http://127.0.0.1:8000/api/ask"
TIMEOUT_SECONDS = 60

# ----------------------------------------------------------------------
# HEALTH POLICY test cases (Individual Health Insurance Policy - UIIC)
# ----------------------------------------------------------------------
HEALTH_POLICY_TESTS = [
    {
        "name": "PED waiting period (the original bug chain)",
        "question": "What is the waiting period for pre-existing diseases (PED) under this policy?",
        "must_contain": ["48 months"],
        "must_not_contain": ["no specific waiting period", "not explicitly mentioned"],
    },
    {
        "name": "Cataract waiting period (reverse-conflation check)",
        "question": "What is the waiting period for cataract surgery?",
        "must_contain": ["24 months"],
        "must_not_contain": [],
    },
    {
        "name": "Room rent + ICU limits (compound question, qualifiers)",
        "question": "What is the room rent limit and ICU charges limit under this policy?",
        "must_contain": ["1%", "2%", "per day"],
        "must_not_contain": [],
    },
    {
        "name": "Hernia/Hysterectomy sub-limit (plan-specific)",
        "question": "What is the sub-limit for hernia and hysterectomy surgery?",
        "must_contain": ["25%", "1,00,000"],
        "must_not_contain": [],
    },
    {
        "name": "Maternity — permanent exclusion wording",
        "question": "Is maternity covered in this policy?",
        "must_contain": ["excl18"],
        "must_not_contain": ["section c", "point number 3"],
    },
    {
        "name": "Infertility/IVF — permanent exclusion wording",
        "question": "Does this policy cover infertility treatment or IVF?",
        "must_contain": ["excl17", "exclud"],
        "must_not_contain": [],
    },
    {
        "name": "Missing scenario — should NOT hallucinate (outside India)",
        "question": "Does this policy cover treatment taken outside India?",
        "must_contain": ["not explicitly mentioned"],
        "must_not_contain": [],
    },
    {
        "name": "Road ambulance — exact figure",
        "question": "What is the maximum amount covered for road ambulance charges?",
        "must_contain": ["2,500"],
        "must_not_contain": [],
    },
    {
        "name": "Free look + cancellation (compound, two different figures)",
        "question": "What is the free look period, and what happens if I cancel the policy after 4 months?",
        "must_contain": ["15 days", "25%"],
        "must_not_contain": [],
    },
    {
        "name": "Topic purity — renewal question should not leak medical exclusions",
        "question": "What is the process for renewing this policy?",
        "must_contain": ["30 days"],
        "must_not_contain": ["maternity", "infertility"],
    },
]

# ----------------------------------------------------------------------
# MOTOR POLICY test cases (Priyanshu Paliwal - New India Assurance)
# NOTE: these will only pass if the motor policy PDF is the one currently
# uploaded/ingested — comment this list out (or set RUN_MOTOR_TESTS=False)
# when testing against the health policy instead.
# ----------------------------------------------------------------------
RUN_MOTOR_TESTS = False

MOTOR_POLICY_TESTS = [
    {
        "name": "IDV — exact figure, no reformatting hallucination",
        "question": "What is IDV?",
        "must_contain": ["753,040"],
        "must_not_contain": ["75,30,400", "75,40,000", "7,53,04,0"],
    },
    {
        "name": "Total damage — should discuss IDV/total-loss, not third-party liability",
        "question": "What if my car get completly damaged?",
        "must_contain": ["753,040"],
        "must_not_contain": ["third party", "third-party"],
    },
    {
        "name": "Missing scenario — should NOT hallucinate (theft)",
        "question": "What if my car is stolen?",
        "must_contain": ["not explicitly mentioned"],
        "must_not_contain": [],
    },
]


def run_test(case: dict) -> tuple:
    """Returns (passed: bool, answer_text: str, failure_reasons: list)"""
    try:
        resp = requests.post(
            API_URL,
            json={"question": case["question"]},
            timeout=TIMEOUT_SECONDS,
        )
    except requests.exceptions.RequestException as e:
        return False, "", [f"Request failed: {e}"]

    if resp.status_code != 200:
        return False, "", [f"HTTP {resp.status_code}: {resp.text[:200]}"]

    try:
        body = resp.json()
        data = body.get("data", body)
        answer = data[0] if isinstance(data, (list, tuple)) else str(data)
    except Exception as e:
        return False, "", [f"Could not parse response: {e}"]

    answer_lower = answer.lower()
    failures = []

    for required in case["must_contain"]:
        if required.lower() not in answer_lower:
            failures.append(f"MISSING expected text: '{required}'")

    for forbidden in case["must_not_contain"]:
        if forbidden.lower() in answer_lower:
            failures.append(f"FOUND forbidden text: '{forbidden}'")

    return (len(failures) == 0), answer, failures


def run_suite(test_cases: list, suite_name: str) -> tuple:
    print(f"\n{'=' * 70}")
    print(f"  {suite_name}")
    print(f"{'=' * 70}")

    passed_count = 0
    failed_count = 0

    for i, case in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] {case['name']}")
        print(f"    Q: {case['question']}")

        passed, answer, failures = run_test(case)

        if passed:
            print(f"    ✅ PASS")
            passed_count += 1
        else:
            print(f"    ❌ FAIL")
            for f in failures:
                print(f"       - {f}")
            print(f"    Got: {answer[:250]}{'...' if len(answer) > 250 else ''}")
            failed_count += 1

    return passed_count, failed_count


def main():
    print("PolicyPilot Regression Test Suite")
    print(f"Target: {API_URL}")

    total_passed = 0
    total_failed = 0

    p, f = run_suite(HEALTH_POLICY_TESTS, "HEALTH POLICY TESTS")
    total_passed += p
    total_failed += f

    if RUN_MOTOR_TESTS:
        p, f = run_suite(MOTOR_POLICY_TESTS, "MOTOR POLICY TESTS")
        total_passed += p
        total_failed += f
    else:
        print(f"\n(Skipping motor policy tests — set RUN_MOTOR_TESTS=True "
              f"and make sure the motor PDF is uploaded to run them)")

    print(f"\n{'=' * 70}")
    print(f"  SUMMARY: {total_passed} passed, {total_failed} failed "
          f"out of {total_passed + total_failed}")
    print(f"{'=' * 70}")

    sys.exit(1 if total_failed > 0 else 0)


if __name__ == "__main__":
    main()