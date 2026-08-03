#!/usr/bin/env python3
"""
Fix hreflang ZH URLs - they should NOT end with -en.
Also fix canonical for files that weren't in the original 52.
"""
import re
import os

BLOG_DIR = "/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/dist/blog"

# Files that were in the original 52 (had Tailwind)
original_52 = [
    'atlantic-seaboard-resilient-cape-town-safe-haven-2026-en.html',
    'cape-town-cruise-terminal-waterfront-investment-en.html',
    'cape-town-dual-engine-income-rental-savings-65-percent-en.html',
    'cape-town-foreshore-rockefeller-overseas-investment-en.html',
    'cape-town-international-capital-en.html',
    'cape-town-listing-supply-crunch-buy-to-let-2026-en.html',
    'cape-town-property-demand-semigration-foreign-buyers-2026-en.html',
    'cape-town-property-investment-2026-en.html',
    'cape-town-property-outlook-2026-overseas-investors-en.html',
    'cape-town-property-resilience-sarb-rate-hike-2026-en.html',
    'cape-town-quality-life-property-demand-2026-en.html',
    'cape-town-quality-of-life-cost-comparison-en.html',
    'cape-town-rental-occupancy-2026-en.html',
    'cape-town-rental-yields-premium-passive-income-2026-en.html',
    'cape-town-sectional-title-investment-guide-2026-en.html',
    'cape-town-southern-suburbs-luxury-property-record-prices-uppers-en.html',
    'cape-town-supply-crunch-sarb-hike-cash-buyer-advantage-en.html',
    'cape-town-tech-semigration-2026-en.html',
    'cape-town-three-structural-trends-h2-2026-en.html',
    'cape-town-uppers-luxury-property-investment-2026-en.html',
    'cape-town-uppers-luxury-scarcity-investment-2026-en.html',
    'cape-town-water-resilience-property-value-growth-en.html',
    'cape-town-waterfront-infrastructure-sea-point-investment-en.html',
    'cape-town-winter-property-strategy-seasonal-investment-en.html',
    'cape-town-winter-rental-strategy-seasonal-yield-2026-en.html',
    'firstrand-uk-exit-en.html',
    'fitch-upgrade-south-africa-cape-town-investment-2026-en.html',
    'foreign-capital-sell-tsmc-cape-town-property-en.html',
    'global-real-estate-recovery-en.html',
    'grandwest-mall-cape-town-infrastructure-investment-en.html',
    'international-buyers-cape-town-foreign-investors-guide-en.html',
    'international-buyers-cape-town-foreign-property-trends-2026-en.html',
    'international-buyers-cape-town-hnw-premium-property-en.html',
    'myciti-phase2a-infrastructure-cape-town-property-investment-en.html',
    'sa-tax-emigration-cape-town-investment-2026-en.html',
    'samsung-strike-supply-chain-vs-cape-town-property-en.html',
    'sarb-july-2026-mpc-preview-cape-town-property-en.html',
    'sarb-mpc-may-2026-property-guide-en.html',
    'sarb-rate-hike-cape-town-foreign-investors-opportunity-en.html',
    'sarb-rate-hike-cape-town-property-safe-haven-2026-en.html',
    'sarb-rate-hold-june-2025-cape-town-property-en.html',
    'south-africa-credit-upgrade-cape-town-investment-2026-en.html',
    'south-africa-high-interest-rate-advantage-cape-town-property-en.html',
    'south-africa-passport-free-travel-en.html',
    'south-africa-remote-work-visa-cape-town-property-demand-2026-en.html',
    'south-africa-transfer-duty-foreign-buyer-cape-town-tax-guide-2026-en.html',
    'stop-loss-emotion-cape-town-passive-income-en.html',
    'taiwan-stock-plunge-capetown-haven-en.html',
    'taiwan-wealthy-overseas-allocation-en.html',
    'vix-stable-cashflow-cape-town-en.html',
    'vix-surge-cape-town-property-hedge-en.html',
    'zar-depreciation-cape-town-property-opportunity-2026-en.html',
]

for f in sorted(os.listdir(BLOG_DIR)):
    if not f.endswith('-en.html'):
        continue
    
    filepath = os.path.join(BLOG_DIR, f)
    with open(filepath, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    modified = False
    
    # Fix hreflang ZH URL - should NOT end with -en
    m = re.search(r'<link\s+rel=["\']alternate["\'][^>]*hreflang=["\']zh-TW["\'][^>]*href=["\']([^"\']+)["\']', content)
    if m:
        url = m.group(1)
        if url.endswith('-en'):
            new_url = url[:-3]
            old_tag = f'hreflang="zh-TW" href="{url}"'
            new_tag = f'hreflang="zh-TW" href="{new_url}"'
            content = content.replace(old_tag, new_tag)
            modified = True
            print(f'{f}: Fixed hreflang ZH: {url} -> {new_url}')
    
    # For files NOT in original 52, restore canonical to not end with -en
    if f not in original_52:
        m = re.search(r'<link\s+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', content)
        if m:
            url = m.group(1)
            if url.endswith('-en'):
                new_url = url[:-3]
                content = content.replace(f'href="{url}"', f'href="{new_url}"')
                modified = True
                print(f'{f}: Restored canonical: {url} -> {new_url}')
        
        # Also fix hreflang EN
        m = re.search(r'<link\s+rel=["\']alternate["\'][^>]*hreflang=["\']en["\'][^>]*href=["\']([^"\']+)["\']', content)
        if m:
            url = m.group(1)
            if url.endswith('-en'):
                new_url = url[:-3]
                old_tag = f'hreflang="en" href="{url}"'
                new_tag = f'hreflang="en" href="{new_url}"'
                content = content.replace(old_tag, new_tag)
                modified = True
                print(f'{f}: Restored hreflang EN: {url} -> {new_url}')
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as fh:
            fh.write(content)
        print(f'  Saved {f}')

print("\nDone fixing URLs")
