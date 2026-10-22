#!/usr/bin/env python3
"""2026-10-22 LINE 選單背景圖 — 3 主題 ComfyUI Qwen-Image 2.1 生成 + 下載"""
import json, os, random, subprocess, sys, time, urllib.request, urllib.parse, uuid

COMFYUI = "http://192.168.0.99:8188"
WORKFLOW = "/Users/dingyao/.hermes/workspaces/saturnian/comfyui_qwen_image21_t2i_workflow.json"
OUT = os.path.expanduser("~/Documents/DingYao-Website/dingyaoadvisory-website/runs/2026-10-22/line-bg/src")
N_RES, N_TEXTENC, N_SAMPLER, N_SAVE = "13", "459:452", "459:458", "461"

TAIL = ("no text, no words, no letters, no numbers, no signage lettering, no logos, "
        "no watermarks, no writing on any surface, no advertising billboards, "
        "no vehicle number plates, no branded equipment")

JOBS = [
    ("bg-banking", "3:2 (Photo)",
     "Professional architectural photograph looking up from a wet stone plaza at a cluster of "
     "glass-curtain-wall bank and corporate office towers in a modern African financial district "
     "at blue hour, cool deep blue sky, grids of faintly lit windows in muted steel blue with a few "
     "dim warm amber interior lights, faint reflections on the polished granite paving, "
     "wide 24mm lens, f/8, deep depth of field, balanced medium-contrast lighting, "
     "rich mid-tone exposure with clear light and shadow separation, muted desaturated cool blue "
     "colour palette with subtle warm highlights, cinematic quiet mood, no bright blown highlights, "
     "no crowds, no people, no parked vehicles, " + TAIL),
    ("bg-property", "3:2 (Photo)",
     "Elevated wide architectural photograph of an affluent coastal residential suburb on a steep "
     "hillside, modern Mediterranean and contemporary white villas with flat roofs cascading down "
     "toward a calm ocean bay, a massive flat-topped sandstone mountain silhouette standing behind "
     "the neighbourhood, blue hour dusk light, deep blue sky, small warm amber window lights and "
     "street lamps glowing as tiny points, soft haze, 24mm lens, f/9, deep depth of field, "
     "balanced medium-contrast lighting, rich mid-tone exposure with clear light and shadow "
     "separation, muted desaturated cool blue colour palette with subtle warm gold highlights, "
     "cinematic quiet mood, no bright blown highlights, no crowds, no boats, " + TAIL),
    ("bg-education", "3:2 (Photo)",
     "Professional architectural photograph of a historic British colonial era university campus "
     "at blue hour: a long sandstone colonnade with repeating arches in the left foreground, a "
     "red-brick collegiate academic building beyond it, a broad manicured green lawn and mature oak "
     "trees in the middle ground, warm lantern light glowing softly under the arches, deep blue "
     "twilight sky, 35mm lens, f/5.6, gentle shallow depth of field on the foreground arcade, "
     "balanced medium-contrast lighting, rich mid-tone exposure with clear light and shadow "
     "separation, muted desaturated cool blue colour palette with subtle warm gold highlights, "
     "calm and welcoming mood, not gloomy, no bright blown highlights, no students, "
     "a plain unmarked stone building facade without any inscriptions or emblems, " + TAIL),
]


def post(url, payload, timeout=60):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def get(url, timeout=30):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read())


def submit(slug, ar, prompt, seed):
    wf = json.load(open(WORKFLOW))
    wf[N_RES]["inputs"]["aspect_ratio"] = ar
    wf[N_RES]["inputs"]["megapixels"] = 1.0
    wf[N_TEXTENC]["inputs"]["prompt"] = prompt
    wf[N_SAVE]["inputs"]["filename_prefix"] = f"20261022-linebg-{slug}"
    wf[N_SAMPLER]["inputs"]["seed"] = seed
    res = post(f"{COMFYUI}/prompt", {"prompt": wf, "client_id": f"jovian-linebg-{uuid.uuid4()}"})
    if res.get("node_errors"):
        raise RuntimeError(json.dumps(res["node_errors"], ensure_ascii=False)[:600])
    return res["prompt_id"]


def main():
    os.makedirs(OUT, exist_ok=True)
    pend = {}
    for slug, ar, prompt in JOBS:
        seed = random.randrange(1, 2**31)
        pid = submit(slug, ar, prompt, seed)
        pend[pid] = (slug, seed)
        print(f"submitted {slug} seed={seed} pid={pid}", flush=True)

    done = {}
    t0 = time.time()
    while pend and time.time() - t0 < 1800:
        time.sleep(8)
        for pid in list(pend):
            try:
                h = get(f"{COMFYUI}/history/{pid}", timeout=20)
            except Exception:
                continue
            if pid not in h:
                continue
            st = h[pid].get("status", {})
            if st.get("status_str") == "error":
                print(f"ERROR {pend[pid][0]}: {json.dumps(st.get('messages'))[:400]}", flush=True)
                del pend[pid]
                continue
            if not st.get("completed"):
                continue
            slug = pend[pid][0]
            for _, out in (h[pid].get("outputs") or {}).items():
                for img in out.get("images", []):
                    fn = img.get("filename")
                    q = urllib.parse.urlencode({"filename": fn, "subfolder": img.get("subfolder", ""),
                                                "type": img.get("type", "output")})
                    dst = os.path.join(OUT, f"{slug}.png")
                    urllib.request.urlretrieve(f"{COMFYUI}/view?{q}", dst)
                    print(f"OK {slug} -> {dst} ({os.path.getsize(dst)} bytes) after {time.time()-t0:.0f}s", flush=True)
                    done[slug] = dst
            del pend[pid]
    print("DONE", json.dumps(done), flush=True)


if __name__ == "__main__":
    main()
