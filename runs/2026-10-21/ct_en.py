import pathlib

def add(path, pairs):
    p = pathlib.Path(path); s = p.read_text(encoding="utf-8"); n = 0
    for key, suffix in pairs:
        i = s.find(key)
        assert i >= 0, f"{path}: key not found -> {code(key)}"
        li_at = s.rfind("<li", 0, i); p_at = s.rfind("<p", 0, i)
        en = s.find("</li>", i) if li_at > p_at else s.find("</p>", i)
        assert en > 0
        s = s[:en] + suffix + s[en:]
        n += 1
    p.write_text(s, encoding="utf-8"); return n

def code(k):
    return k[:45]

en_a = [
 ("About 18 months — and", " This article is written around Cape Town and the Western Cape as the base, with Hilton College and Michaelhouse kept as the KZN comparison, because Cape Town is where most Taiwanese families actually settle."),
 ("Mapped onto a family calendar, the South African cycle feels much closer.",
  " In Cape Town the same 2028 start would mean signing a Southern Suburbs lease in October or November 2027 so the family can move in for January."),
 ("Registration</strong>: get into the school's database",
  " (in Cape Town the equivalent step is answering the entrance-exam invitation in November of Grade 6)"),
 ("Visit and interview</strong>: campus tour",
  " (Cape Town day schools usually host this on an open day or in an individual family meeting)"),
 ("Assessment</strong>: around January",
  " (in Cape Town it falls in February of Grade 7, English and Mathematics)"),
 ("Offer</strong>: February to April",
  " (Cape Town keeps a similar rhythm but without the boarding-bed step)"),
 ("Laid out side by side, the published 2028 Grade 8 dates",
  " Those are the KZN milestones; the Cape Town counterpart is in Section 3."),
 ("Two things stand out.", " In Cape Town those nine months absorb the Southern Suburbs lease, the notarised guardianship letter and the school-run route."),
 ("Because the cut-off at this South African school is more than a year ahead",
  " Cape Town day schools carry no such multi-year cut-off, but the entrance exam sits in February of Grade 7 — miss it and the family waits another year."),
 ("South African selection criteria make late decisions harder still.",
  " Cape Town independent schools weigh the same evidence, replacing the boarding interview with a family interview."),
 ("A detail easily missed in the South African system",
  " In Cape Town mid-year transfers also depend on vacancies, while Bishops opens its 156 Grade 8 places once a year."),
 ("There are options in the South African system",
  " Cape Town adds one more path: enter a day school first, then move to boarding if the family arrangement changes."),
 ("What these three South African fallbacks share",
  " For a Cape Town family, the 18-month countdown becomes twelve months plus the February of Grade 7 entrance exam."),
 ("Guardianship stays with the parents",
  " In Cape Town this matters more, because most schools are day schools: there is no housemaster at all, so the local responsible adult carries more weight."),
 ("A parent accompanies the child", " The Southern Suburbs rent bands are in Section 6."),
 ("A relative or family friend on the ground", " Cape Town schools usually also require that person to live within a reasonable drive."),
 ("A school-approved guardianship service", " Most Cape Town day schools refer aftercare and guardianship providers, charged separately."),
 ("The three recurring gaps in South African visa files",
  " Lodging in Cape Town, the most common request for further documents is an authorisation that never mentioned medical consent."),
 ("The South African study visa sits under section 13",
  " Cape Town acceptance letters usually arrive during Grade 7, which lines up with the lodging window a year before entry."),
 ("South African fees and forms move too",
  " Cape Town applicants follow the same fee schedule, plus the visa centre's separate service charge."),
 ("The South African school year opens in mid-January",
  " Cape Town independent and private schools shift slightly inside that frame."),
 ("South African independent schools shift these dates slightly",
  " For Cape Town families the two dates that must line up are the lease start and the first day of Term 1."),
 ("That last point is the most under-estimated.",
  " Cape Town day schools have no boarding house to close, but mid-term and December breaks still arrive and the child still needs someone."),
 ("South Africa private school fees are not one number.",
  " In Cape Town there is a sixth layer: rent."),
 ("The payment rhythm also needs planning",
  " Cape Town day schools usually bill termly rather than annually, a different rhythm from boarding."),
 ("Traditional boarding schools</strong>: an 18-month admission cycle",
  " The Cape Town equivalent — an independent day school — runs on half that lead time."),
]
print("en-a:", add("parts/en-body-a.html", en_a))

en_b = [
 ("It varies by South African school", " In Cape Town day schools the first real node is November of Grade 6."),
 ("An interview, yes, and some South African schools add an assessment.",
  " Bishops in Cape Town adds an entrance exam in English and Mathematics."),
 ("Legal guardianship stays with the parents and does not move",
  " In Cape Town, day schools ask for a reachable local adult rather than a housemaster."),
 ("Beyond the standard South African study visa pack",
  " Lodging in Cape Town, the accommodation proof is usually the Southern Suburbs lease."),
 ("September or October of the year before entry",
  " In Cape Town the entrance exam in February of Grade 7 is what unlocks that window."),
 ("Based on the two schools' published 2026 figures",
  " A Cape Town day school replaces part of that structure with rent plus daily transport."),
 ("This article compiles public information",
  " Cape Town schools and Western Cape public schools revise their rules annually; check each school's own site."),
]
print("en-b:", add("parts/en-body-b.html", en_b))
