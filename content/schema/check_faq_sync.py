"""Compare FAQ Q/A text in schema/*.html against the visible **Q:**/**A:** pairs in the content pack."""
import json, re, sys
pack = open(sys.argv[1], encoding="utf-8").read()
pages = {"home.html": "## Page 1: Home", "pricing.html": "## Page 2: Pricing"}
def norm(s): return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()
def section(name):
    start = pack.index(name); nxt = pack.find("\n## Page", start + 1)
    return pack[start: nxt if nxt != -1 else len(pack)]
fails = 0
for fname, heading in pages.items():
    vis = re.findall(r"\*\*Q:\*\* (.+?)\n\*\*A:\*\* (.+?)\n", section(heading))
    raw = open(f"schema/{fname}", encoding="utf-8").read()
    block = re.search(r"<script[^>]*>(.*?)</script>", raw, re.S).group(1)
    data = json.loads(block)
    faq = next(n for n in data["@graph"] if n["@type"] == "FAQPage")["mainEntity"]
    print(f"{fname}: {len(vis)} visible, {len(faq)} in schema")
    for i, (q, a) in enumerate(vis):
        sq, sa = (norm(faq[i]["name"]), norm(faq[i]["acceptedAnswer"]["text"])) if i < len(faq) else ("", "")
        for label, v, s in (("Q", norm(q), sq), ("A", norm(a), sa)):
            if v == s: print(f"  PASS {label}{i+1}")
            else:
                fails += 1; print(f"  FAIL {label}{i+1}\n    visible: {v}\n    schema : {s}")
    if len(vis) != len(faq): fails += 1; print("  FAIL count mismatch")
print("RESULT:", "ALL PASS" if fails == 0 else f"{fails} mismatch(es)")
