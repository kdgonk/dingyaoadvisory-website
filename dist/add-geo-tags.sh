#!/bin/bash
# 泰坦人 - SEO GEO 標籤批量添加腳本

# GEO 標籤模板
GEO_TAGS='
<meta content="TW-TXG" name="geo.region"/>
<meta content="台中市" name="geo.placename"/>
<meta content="24.163;120.647" name="geo.position"/>
<meta content="24.163, 120.647" name="ICBM"/>'

# 需要添加 GEO 標籤的頁面
PAGES=(
    "education.html"
    "education-en.html"
    "retirement.html"
    "retirement-en.html"
    "residency.html"
    "residency-en.html"
    "assets.html"
    "assets-en.html"
    "privacy.html"
    "privacy-en.html"
    "terms.html"
    "terms-en.html"
    "blog.html"
    "blog-en.html"
    "blog/cape-town-property-investment-2026.html"
)

for page in "${PAGES[@]}"; do
    if [ -f "$page" ]; then
        # 檢查是否已有 GEO 標籤
        if ! grep -q 'geo.region' "$page"; then
            # 在 <meta name="author"> 後面插入 GEO 標籤
            sed -i.bak '/<meta content="鼎曜國際顧問有限公司" name="author"\/>/a\'"$GEO_TAGS" "$page"
            echo "✓ 已添加 GEO 標籤: $page"
        else
            echo "  跳過（已有 GEO 標籤）: $page"
        fi
    else
        echo "  檔案不存在: $page"
    fi
done

# 清理備份檔案
rm -f *.bak blog/*.bak

echo ""
echo "完成！"