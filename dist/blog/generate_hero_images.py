#!/usr/bin/env python3
"""Generate 4 hero images for blog articles using FAL.ai, upload to R2, update HTML files."""

import os
import json
import time
import subprocess
import re
from PIL import Image
from io import BytesIO
import requests

FAL_KEY = "4c7e2be4-5b2d-4c2e-8fc1-f8fc7f5d3b42:c36ef4f0a0ad0b6b3c2f9c5c5f12c8e4"
os.environ["FAL_KEY"] = FAL_KEY

from fal_client import submit as fal_submit

OUTPUT_DIR = "/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/dist/blog/images"
BLOG_DIR = "/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/dist/blog"
R2_BASE = "https://assets.dingyaoadvisory.tw/blog/images"

# Model: FLUX 2 Pro for best photorealism
MODEL = "fal-ai/flux-2-pro"

def generate_image(prompt, filename, max_retries=3):
    """Generate image via FAL, download, convert to 1200x630 webp."""
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    for attempt in range(max_retries):
        print(f"\n=== Generating {filename} (attempt {attempt+1}) ===")
        print(f"Prompt: {prompt[:100]}...")
        
        try:
            handle = fal_submit(
                MODEL,
                arguments={
                    "prompt": prompt,
                    "image_size": "landscape_16_9",
                    "num_inference_steps": 50,
                    "guidance_scale": 4.5,
                    "num_images": 1,
                    "output_format": "png",
                    "enable_safety_checker": False,
                    "safety_tolerance": "5",
                    "sync_mode": True,
                }
            )
            
            result = handle.get()
            print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else type(result)}")
            
            # Get image URL from result
            images = result.get("images", [])
            if not images:
                print(f"ERROR: No images in result: {json.dumps(result, indent=2)[:500]}")
                continue
            
            image_url = images[0].get("url")
            if not image_url:
                print(f"ERROR: No URL in image data: {images[0]}")
                continue
            
            print(f"Downloading from: {image_url}")
            resp = requests.get(image_url, timeout=60)
            resp.raise_for_status()
            
            # Open with PIL
            img = Image.open(BytesIO(resp.content))
            print(f"Original size: {img.size}")
            
            # Resize to 1200x630 (og:image standard)
            img = img.resize((1200, 630), Image.LANCZOS)
            
            # Save as webp
            img.save(output_path, "WEBP", quality=85)
            print(f"Saved: {output_path} ({os.path.getsize(output_path)} bytes)")
            return True
            
        except Exception as e:
            print(f"ERROR on attempt {attempt+1}: {e}")
            import traceback
            traceback.print_exc()
            if attempt < max_retries - 1:
                time.sleep(5)
    
    return False


def upload_to_r2(filename):
    """Upload image to R2 using rclone."""
    local_path = os.path.join(OUTPUT_DIR, filename)
    r2_path = f"dingyao-r2:dingyaoadvisory/blog/images/{filename}"
    
    print(f"Uploading {filename} to R2...")
    result = subprocess.run(
        ["rclone", "copy", local_path, r2_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Upload error: {result.stderr}")
        return False
    print(f"Uploaded: {R2_BASE}/{filename}")
    return True


def update_html_file(filepath, hero_filename):
    """Update all image references in an HTML file."""
    r2_url = f"{R2_BASE}/{hero_filename}"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changes = 0
    
    # 1. Update og:image
    og_pattern = r'(<meta property="og:image" content=")[^"]*(")'
    if re.search(og_pattern, content):
        content = re.sub(og_pattern, f'\\1{r2_url}\\2', content)
        changes += 1
    
    # 2. Update twitter:image
    tw_pattern = r'(<meta name="twitter:image" content=")[^"]*(")'
    if re.search(tw_pattern, content):
        content = re.sub(tw_pattern, f'\\1{r2_url}\\2', content)
        changes += 1
    
    # 3. Update JSON-LD image
    jsonld_pattern = r'("image": ")[^"]*(")'
    if re.search(jsonld_pattern, content):
        content = re.sub(jsonld_pattern, f'\\1{r2_url}\\2', content)
        changes += 1
    
    # 4. Update img src (hero image)
    img_pattern = r'(<img src=")[^"]*hero\.webp(")'
    if re.search(img_pattern, content):
        content = re.sub(img_pattern, f'\\1{r2_url}\\2', content)
        changes += 1
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  Updated {filepath}: {changes} changes")
    return changes > 0


# ============================================================
# Image 1: Semigration 2.0 - Cape Town skyline with Table Mountain
# ============================================================
prompt_1 = """Aerial panoramic view of Cape Town city skyline at golden hour, with the iconic flat-topped Table Mountain dominating the background. Modern glass high-rise buildings in the foreground, natural fynbos vegetation on the mountain slopes. The city stretches between mountain and ocean. Dark moody tones, deep navy and warm amber lighting, cinematic quality. Photorealistic, ultra high quality, architectural photography style. No text, no labels, no watermark anywhere."""

# ============================================================
# Image 2: SARB holds rate - SARB building / financial district
# ============================================================
prompt_2 = """The South African Reserve Bank building in Pretoria, a striking modern architectural landmark with its distinctive angular design and glass facade. Shot from low angle looking up, dramatic sky with moody clouds. Dark sophisticated tones, deep blues and greys. Professional financial district atmosphere. Photorealistic, ultra high quality, architectural photography. No text, no labels, no watermark anywhere."""

# ============================================================
# Image 3: Inflation 5% - V&A Waterfront bustling scene
# ============================================================
prompt_3 = """The vibrant V&A Waterfront in Cape Town at dusk, with the iconic clock tower, luxury shops, outdoor restaurants with patrons, and the working harbor with boats. Table Mountain visible in the background. Warm golden lighting from street lamps and shop windows reflecting on the water. Bustling economic activity, people walking and dining. Dark moody tones with warm amber highlights. Photorealistic, ultra high quality. No text, no labels, no watermark anywhere."""

# ============================================================
# Image 4: Durbanville - suburban residential street
# ============================================================
prompt_4 = """A peaceful tree-lined residential street in Durbanville, Cape Town's northern suburbs. Modern Cape Dutch style homes with thatched roofs, manicured gardens with indigenous plants, oak trees creating a canopy over the road. Warm golden afternoon sunlight filtering through leaves. A wine farm vineyard visible in the distance. Dark moody tones with warm amber highlights. Suburban luxury, quality of life atmosphere. Photorealistic, ultra high quality. No text, no labels, no watermark anywhere."""


# Image definitions
images = [
    {
        "prompt": prompt_1,
        "filename": "cape-town-semigration-2-0-maturing-market-2026-hero.webp",
        "articles": [
            "cape-town-semigration-2-0-maturing-market-2026.html",
            "cape-town-semigration-2-0-maturing-market-2026-en.html",
        ]
    },
    {
        "prompt": prompt_2,
        "filename": "sarb-holds-rate-july-2026-cape-town-property-impact-hero.webp",
        "articles": [
            "sarb-holds-rate-july-2026-cape-town-property-impact.html",
            "sarb-holds-rate-july-2026-cape-town-property-impact-en.html",
        ]
    },
    {
        "prompt": prompt_3,
        "filename": "south-africa-inflation-5-percent-cape-town-property-2026-hero.webp",
        "articles": [
            "south-africa-inflation-5-percent-cape-town-property-2026.html",
            "south-africa-inflation-5-percent-cape-town-property-2026-en.html",
        ]
    },
    {
        "prompt": prompt_4,
        "filename": "cape-town-northern-suburbs-boom-durbanville-13-percent-2026-hero.webp",
        "articles": [
            "cape-town-northern-suburbs-boom-durbanville-13-percent-2026.html",
            "cape-town-northern-suburbs-boom-durbanville-13-percent-2026-en.html",
        ]
    },
]

# Generate all images
all_success = True
for img in images:
    success = generate_image(img["prompt"], img["filename"])
    if not success:
        print(f"FAILED to generate {img['filename']}")
        all_success = False
    else:
        # Upload to R2
        upload_to_r2(img["filename"])

if not all_success:
    print("\n⚠️ Some images failed to generate. Check errors above.")
    exit(1)

# Update all HTML files
print("\n=== Updating HTML files ===")
for img in images:
    for article in img["articles"]:
        filepath = os.path.join(BLOG_DIR, article)
        if os.path.exists(filepath):
            update_html_file(filepath, img["filename"])
        else:
            print(f"  WARNING: {filepath} not found!")

print("\n=== DONE ===")
