<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
                xmlns:html="http://www.w3.org/TR/REC-html40"
                xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
                xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <title>網站地圖 Sitemap - DYA Ding Yao Advisory</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <style type="text/css">
          body { 
            font-family: 'Inter', -apple-system, sans-serif; 
            background-color: #0A0E17; 
            color: #F5F0E8; 
            margin: 0; 
            padding: 40px 24px; 
            line-height: 1.6;
          }
          .container { max-width: 1000px; margin: 0 auto; }
          h1 { 
            color: #C9A84C; 
            font-family: 'Playfair Display', serif; 
            font-size: 2rem; 
            border-bottom: 1px solid rgba(201,168,76,0.2);
            padding-bottom: 16px;
            margin-bottom: 8px;
          }
          .description { color: #8B8FA3; font-size: 0.9rem; margin-bottom: 32px; }
          table { width: 100%; border-collapse: collapse; background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(201,168,76,0.1); }
          th, td { padding: 16px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.05); }
          th { 
            color: #C9A84C; 
            font-weight: 600; 
            font-size: 0.9rem;
            letter-spacing: 1px;
            background: rgba(201,168,76,0.05);
          }
          td { font-size: 0.9rem; }
          a { color: #F5F0E8; text-decoration: none; transition: color 0.3s; }
          a:hover { color: #C9A84C; }
          .url-path { color: #8B8FA3; font-size: 0.8rem; display: block; margin-top: 4px; }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>網站地圖 Sitemap</h1>
          <p class="description">此頁面為 DYA Ding Yao Advisory 的完整網站架構。您可點擊下方連結前往對應頁面。</p>
          <table>
            <tr>
              <th>頁面連結 (URL)</th>
              <th>最後更新時間 (Last Modified)</th>
            </tr>
            <xsl:for-each select="sitemap:urlset/sitemap:url">
              <tr>
                <td>
                  <a href="{sitemap:loc}"><xsl:value-of select="sitemap:loc"/></a>
                </td>
                <td style="color:#8B8FA3;">
                  <xsl:value-of select="sitemap:lastmod"/>
                </td>
              </tr>
            </xsl:for-each>
          </table>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
