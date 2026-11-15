"""Run the official engineio/math-sdk RGS verification functions
(utils/rgs_verification.py, MIT licence) against our exported files.

Usage: python verify_with_official_sdk.py <path-to-math-sdk-clone> <publish_files dir> [out.json]
The math-sdk is NOT vendored in this repo; clone it with
  git clone --depth 1 https://github.com/engineio/math-sdk.git
"""
import json
import os
import sys

sdk, pub = sys.argv[1], sys.argv[2]
out = sys.argv[3] if len(sys.argv) > 3 else None
sys.path.insert(0, os.path.abspath(sdk))
from utils import rgs_verification as rv  # noqa: E402

index = json.load(open(os.path.join(pub, "index.json")))
stats = []
for mode in index["modes"]:
    lut = os.path.join(pub, mode["weights"])
    books = os.path.join(pub, mode["events"])
    win_dist, lut_payouts, wsum, min_win, max_win = rv.verify_lookup_format(lut)
    book_payouts, n_events = rv.verify_books_and_payout_mults(books)
    rv.compare_payout_values(book_payouts, lut_payouts)
    s = rv.get_lut_statistics(mode["name"], win_dist, mode["cost"], lut_payouts, wsum, min_win, max_win, len(lut_payouts))
    s.name = mode["name"]
    stats.append(s)
    print(f"[{mode['name']}] format OK, books==LUT payouts OK, {len(lut_payouts)} rounds, {n_events} events")
issues = rv.verify_submission_limits(stats)
risk = {s.name: rv.get_risk_failures(s) for s in stats}
rv.verify_studio_limits(stats)
summary = {
    "sdk_commit": os.popen(f"git -C {sdk} rev-parse HEAD").read().strip(),
    "submission_issues": issues,
    "risk_failures": {k: {c: [list(map(str, m)) for m in v] for c, v in d.items()} for k, d in risk.items()},
    "modes": {s.name: {k: (float(v) if isinstance(v, (int, float)) else None) for k, v in s.to_dict().items() if k not in ("win_distribution", "unique_wins")} for s in stats},
}
print(json.dumps({k: summary[k] for k in ("sdk_commit", "submission_issues", "risk_failures")}, indent=2))
for n, m in summary["modes"].items():
    print(n, {k: m[k] for k in ("rtp", "std", "max_win", "non_zero_hr", "prob_less_bet", "m2m") if k in m})
if out:
    json.dump(summary, open(out, "w"), indent=2)
