import pathlib

def rep(path, pairs):
    p = pathlib.Path(path); s = p.read_text(encoding="utf-8"); n = 0
    for old, new in pairs:
        assert old in s, f"{path}: missing -> {old[:45]}"
        s = s.replace(old, new, 1); n += 1
    p.write_text(s, encoding="utf-8"); return n

a = [
 ("Key summary:", "Key summary (built around Cape Town and the Western Cape, with KZN boarding kept as the comparison):"),
 ("Most parents start with", "Most parents weighing Cape Town start with"),
 ("At a South African boarding school this covers tuition, food and board",
  "At a Cape Town day school the annual fee covers tuition only — food, board and rent sit outside it. At a South African boarding school this covers tuition, food and board"),
 ("Beyond the annual fee, South African schools charge for books",
  "In Cape Town a day school adds daily transport or a school bus on top. Beyond the annual fee, South African schools charge for books"),
 ("Paid when accepting a South African school's offer",
  "Cape Town independent schools charge the same non-refundable acceptance fee, and it is not returned if the visa is refused. Paid when accepting a South African school's offer"),
 ("Applies to families living outside South Africa: about one and a half terms' fees",
  "Cape Town day schools usually skip this deposit and bill termly instead. Applies to families living outside South Africa: about one and a half terms' fees"),
 ("Stay on the South African school's list while applying elsewhere.",
  "In Cape Town the equivalent is holding a place at one day school while testing another."),
]
print("en-a:", rep("parts/en-body-a.html", a))

c = [
 ("Put rent back into the decision: a family choosing the <strong>Southern Suburbs</strong>",
  "Put rent back into the decision: a family choosing Cape Town's <strong>Southern Suburbs</strong>"),
 ("It is to compare: <strong>the same capital buys a two-bedroom in the Southern Suburbs to live in and partly let, or a one-bedroom on the Atlantic Seaboard",
  "It is to compare: <strong>the same capital buys a two-bedroom in Cape Town's Southern Suburbs to live in and partly let, or a one-bedroom on the Atlantic Seaboard"),
 ("(Sources: Bishops Admissions and Entrance Exam pages, 2026; Somerset College Admissions and Boarding pages, 2026; SACS classification per",
  "(Sources: Bishops Admissions and Entrance Exam pages, Cape Town, 2026; Somerset College Admissions and Boarding pages, 2026; SACS classification per"),
 ("<li><strong>A parent accompanies the child</strong>: the most direct route, but the parent's own permission",
  "<li><strong>A parent accompanies the child</strong> in Cape Town: the most direct route, but the parent's own permission"),
 ("Admits <strong>156 boys</strong> into Grade 8 across six sets of 26",
  "Admits <strong>156 boys</strong> into Grade 8 at its Rondebosch, Cape Town campus across six sets of 26"),
]
print("en-c:", rep("parts/en-body-c.html", c))
