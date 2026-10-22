# 反向內連計畫（給泰坦人，部署本文時一併執行）

**日期**：2026-10-21 | **交付對象**：泰坦人（部署）
**來源**：撞題表規則 4「重疊 <50% 且切角可分 → 差異化，兩頁雙向內連」——本文已單向連出，缺反向這一條。

## 為什麼要做
`/blog/taiwan-parents-choosing-south-africa-private-schools` 目前在 GSC 以「南非留學」排 **pos 6.8**（8 曝光 / 0 點擊）。
它是本文最近的鄰頁，反向內連可把該頁的既有訊號導到新的「申請時程」頁，同時讓該頁訪客多一個「下一步」出口（時程比選校更早卡關）。

## 要改 2 個檔案（各 1 行）

### ① ZH：`dist/blog/taiwan-parents-choosing-south-africa-private-schools.html`
在 `<h2>相關閱讀</h2>` 之後的 `<ul>` 內，**插入為第一個 `<li>`**：

```html
<li><a href="/blog/south-africa-boarding-school-admission-timeline-2026" title="南非寄宿學校申請時程與監護安排">南非寄宿學校申請時程與監護安排</a>——18 個月時程表、監護人與學生簽證連動。</li>
```

### ② EN：`dist/blog/taiwan-parents-choosing-south-africa-private-schools-en.html`
在 `<h2>Related reading</h2>` 之後的 `<ul>` 內，**插入為第一個 `<li>`**：

```html
<li><a href="/blog/south-africa-boarding-school-admission-timeline-2026-en" title="South Africa boarding school admission timeline and guardianship">South Africa boarding school admission timeline and guardianship</a> — the 18-month calendar, guardian rules and study visa sequence.</li>
```

## 驗收
```bash
grep -c 'south-africa-boarding-school-admission-timeline-2026' dist/blog/taiwan-parents-choosing-south-africa-private-schools.html      # ≥1
grep -c 'south-africa-boarding-school-admission-timeline-2026-en' dist/blog/taiwan-parents-choosing-south-africa-private-schools-en.html # ≥1
```
- 兩頁既有內連不得因此減少（插入不取代）
- 錨文字須維持上列（用目標頁要排的關鍵字，不可改「點這裡」）
- 兩頁其餘內容不動；改完跑 `scripts/sort_blog_cards.py --check`（若觸及列表頁）

## 不做也可以的情況
若本週部署排程吃緊，**反向內連可延後一批**，但不要忘記 —— 少了這條，本文在規則 4 下屬「單向差異化」，SEO 效益會打折。
