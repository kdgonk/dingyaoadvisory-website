# 2026-10-21 圖片交付（木星人）

**日期**：2026-10-21 | **交付對象**：泰坦人（部署確認 CDN 路徑）／火星人（文章已引用，無需改 HTML）
**作者**：木星人 ♃

## 一、今日文章配圖（4 檔，已上線並驗證）

文章：`south-africa-boarding-school-admission-timeline-2026`（中／英共用同一組圖）

| 完整 URL | HTTP | bytes | 尺寸 |
|---|---|---|---|
| https://assets.dingyaoadvisory.tw/blog/images/south-africa-boarding-school-admission-timeline-2026-hero.webp | 200 | 353,626 | 1920×1080 |
| https://assets.dingyaoadvisory.tw/blog/images/south-africa-boarding-school-admission-timeline-2026-s1.webp | 200 | 59,064 | 1920×1080 |
| https://assets.dingyaoadvisory.tw/blog/images/south-africa-boarding-school-admission-timeline-2026-s2.webp | 200 | 52,616 | 1920×1080 |
| https://assets.dingyaoadvisory.tw/blog/images/south-africa-boarding-school-admission-timeline-2026-s3.webp | 200 | 149,588 | 1920×1080 |

- 逐檔獨立 curl 驗證：HTTP 200 且 `size_download` == 本地 `stat -f%z`，並以 PIL 重新解碼確認格式 WEBP、尺寸正確。
- Cloudflare purge：4/4 成功（`purge_cache files`），purge 後再次驗證仍 200 且 bytes 相符。
- 本機複本：`runs/2026-10-21/images/`（8 檔全在，可直接給 build 用）。

## 二、白皮書封面底圖（4 檔，純背景無文字）

疊字由土星人後製，**底圖本身零文字**。

| 完整 URL | HTTP | bytes | 尺寸 |
|---|---|---|---|
| https://assets.dingyaoadvisory.tw/whitepapers/covers/wp-property-cover.webp | 200 | 123,918 | 1600×2000 |
| https://assets.dingyaoadvisory.tw/whitepapers/covers/wp-education-cover.webp | 200 | 169,560 | 1600×2000 |
| https://assets.dingyaoadvisory.tw/whitepapers/covers/wp-rental-cover.webp | 200 | 61,274 | 1600×2000 |
| https://assets.dingyaoadvisory.tw/whitepapers/covers/wp-banking-cover.webp | 200 | 47,434 | 1600×2000 |

## 三、驗收數據（像素實測）

| 檔 | mean | sd |
|---|---|---|
| hero | 75.4 | 70.1 |
| s1 | 74.3 | 72.6 |
| s2 | 116.7 | 77.3 |
| s3 | 39.6 | 32.0（原 24.5，gamma 0.75 提亮以保留暗部細節） |
| wp-property | 38.0 | 29.0 |
| wp-education | 24.6 | 34.6 |
| wp-rental | 28.0 | 28.0–35.3 |
| wp-banking | 24.4 | 24.0 |

封面 mean 24–38 為規格要求（深海軍藍 #0b132b、低對比、上方 1/3 乾淨給標題），非失誤。

## 四、文字檢核方式

1. 全圖 vision 逐張檢視（含人物是否可辨識、是否有中文元素）。
2. 對高風險區域裁切放大 **3×** 複核：hero 建築立面、wp-property 房屋群、wp-rental 遠景天際線、wp-education 拱廊石材。
3. 判定標準：看得懂的字元才算違規；石紋、窗框、欄杆造成的短筆畫視為雜訊。
4. 結果：8/8 零可辨識文字／字母／數字／標誌／招牌／書本封面；人物皆為側背影或景深外，無可辨識臉孔；無中文元素。
