#!/bin/bash
# 批量為 HTML 檔案添加 APAC HUB 標籤

DIST_DIR="/Users/dingyao/.openclaw/workspace/dingyaoadvisory-website/dist"

# 需要添加 APAC HUB 的檔案
FILES=(
    "education.html"
    "partners.html"
    "platform.html"
    "retirement.html"
    "residency.html"
)

for file in "${FILES[@]}"; do
    filepath="$DIST_DIR/$file"
    if [ -f "$filepath" ]; then
        # 檢查是否已有 APAC HUB
        if ! grep -q "APAC HUB" "$filepath"; then
            echo "Processing: $file"
            # 在 </div> 後面的 DING YAO 區塊後添加 APAC HUB
            sed -i '' 's|<span class="text-\[0.55rem\] text-gray-400 font-medium tracking-\[0.1em\] uppercase leading-tight">ADVISORY</span>|<span class="text-[0.55rem] text-gray-400 font-medium tracking-[0.1em] uppercase leading-tight">ADVISORY</span>\n                        </div>\n                        <span class="ml-2 text-[0.5rem] bg-[#0F172A] text-white px-1.5 py-0.5 rounded border border-gray-700 font-bold tracking-widest uppercase opacity-80">APAC HUB</span>|' "$filepath"
        fi
    fi
done

echo "Done!"