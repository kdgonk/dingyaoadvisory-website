# Image Brief — south-africa-boarding-school-admission-timeline-2026

**日期**：2026-10-21 | **交付對象**：木星人（產圖）→ 泰坦人（部署時確認 CDN 路徑）
**文章**：`runs/2026-10-21/south-africa-boarding-school-admission-timeline-2026.html`（＋`-en` 共用同一組圖）

## 硬規則
- 全部 **.webp**，檔名如列，上傳至 `https://assets.dingyaoadvisory.tw/blog/images/`
- 提示詞**不得包含任何文字要求**；成品**不可出現任何可辨識文字、字母、數字、標誌**（含招牌、書本封面、文件內容、日曆數字）
- 中英文版共用同一組圖，因此**不可出現中文元素**
- 人物一律為側背影或景深模糊，避免可辨識肖像
- 色調統一：黃昏／暖金色＋深藍灰陰影，與站體深色主題一致

| 檔名 | 用途 | 尺寸 | Prompt（英文，直接餵產圖） |
|---|---|---|---|
| `south-africa-boarding-school-admission-timeline-2026-hero.webp` | Hero（文章頂圖＋og:image＋twitter:image＋JSON-LD image） | 1920×1080 | `Editorial photograph of a historic South African boarding school campus at golden hour: weathered stone main building with gabled roofline, wide manicured lawns, tall established trees, a few teenage students in dark blazers walking away from camera in the middle distance, soft warm late-afternoon light, long shadows, shallow atmospheric haze, cinematic depth of field, muted navy and warm gold palette, no text, no lettering, no signage, no logos` |
| `south-africa-boarding-school-admission-timeline-2026-s1.webp` | S1 背景（申請時程／18 個月節點） | 1920×1080 | `Close-up editorial photograph of a parent's hands marking a blank paper planner with a thin gold pen on a dark walnut desk, soft warm desk lamp light, shallow depth of field, blank unmarked pages with no legible writing, a pair of reading glasses and a cup of tea slightly out of focus, calm and deliberate mood, navy and warm amber palette, no text, no numbers, no lettering, no logos` |
| `south-africa-boarding-school-admission-timeline-2026-s2.webp` | S2 背景（監護人安排／學生簽證文件） | 1920×1080 | `Editorial photograph over the shoulder of two parents reviewing a plain folder of documents across a table from an adviser whose face is out of frame, unbranded passport covers and a small stack of blank papers, warm interior light from a window, soft focus, hands only, navy suit tones with warm gold highlights, no text, no lettering, no numbers, no logos` |
| `south-africa-boarding-school-admission-timeline-2026-s3.webp` | S3 背景（費用結構五層） | 1920×1080 | `Still-life editorial photograph of a plain leather-bound ledger closed with a thin ribbon, a vintage brass calculator with a blank face and a fountain pen on dark oak, single warm side light, deep shadows, elegant restrained composition, navy and gold palette, no text, no numbers, no lettering, no logos` |
| `south-africa-boarding-school-admission-timeline-2026-s4.webp` | S4 背景（開普敦與西開普學校分級／申請要點） | 1920×1080 | `Editorial photograph of a Cape Town Southern Suburbs school campus: whitewashed Cape Dutch gable building beside a modern glass classroom wing, oak trees casting dappled shade on a stone walkway, two parents seen from behind at a distance looking towards the entrance, Table Mountain silhouette faintly visible on the horizon, warm late afternoon light, navy and warm gold palette, no text, no lettering, no signage, no logos, no flags` |

## 驗收（木星人自檢後回報）
1. **5 檔**皆 .webp，檔名逐字相同（含 `-hero` / `-s1` / `-s2` / `-s3` / `-s4`）
2. `curl -o /dev/null -w "%{http_code}"` 每檔 = 200
3. vision 檢查：**無任何可辨識文字／數字／品牌標誌**、無中文元素
4. hero 為 16:9，section 圖 s1–s3 可 16:9 裁切不切到主體

## 備註（給泰坦人）
- 文章 HTML 已寫入 4 個圖檔路徑，圖未上傳前 hero 會顯示為深色底（正常，非破圖）
- 內文 4 個 section 有背景圖（s1–s4；s4 為 2026-10-21 補開普敦章節時新增），其餘 section 為純色
