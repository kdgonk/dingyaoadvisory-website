#!/usr/bin/env python3
"""
Markdown to HTML Converter for Titan (泰坦人)
Converts Marsian's Markdown articles to HTML using blog-template.html

Usage:
    python3 md_to_html.py --input /path/to/article.md --output /path/to/output.html
    python3 md_to_html.py --batch /path/to/articles/ --output /path/to/blog/
"""

import os
import sys
import re
import yaml
from pathlib import Path
from datetime import datetime

# Configuration
TEMPLATE_FILE = Path('/Users/dingyao/.openclaw/workspace/dingyaoadvisory-website/dist/blog/blog-template.html')

# Category mapping
CATEGORIES = {
    '科技產業': 'investment',
    '生活品質': 'lifestyle',
    '市場分析': 'investment',
    '教育留學': 'education',
    '退休生活': 'lifestyle',
    '身分規劃': 'residency',
}

CATEGORY_LABELS = {
    '科技產業': '科技產業',
    '生活品質': '生活品質',
    '市場分析': '市場分析',
    '教育留學': '教育留學',
    '退休生活': '退休生活',
    '身分規劃': '身分規劃',
}


def parse_markdown(filepath):
    """Parse Markdown file and extract YAML front matter + content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract YAML front matter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            yaml_content = parts[1].strip()
            body = parts[2].strip()
            
            # Parse YAML
            metadata = yaml.safe_load(yaml_content)
            return metadata, body
    
    return None, content


def markdown_to_html(md_text):
    """Convert Markdown to HTML (basic conversion)."""
    html = md_text
    
    # Headers (must be done in order H3 -> H2 -> H1 to avoid double replacement)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Bold and italic
    html = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Blockquotes
    html = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
    
    # Horizontal rules
    html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)
    
    # Tables (basic conversion)
    def convert_table(match):
        table_text = match.group(0)
        lines = table_text.strip().split('\n')
        html_table = '<table class="min-w-full divide-y divide-gray-200 mb-6">\n'
        
        for i, line in enumerate(lines):
            if '---' in line:
                continue
            
            cells = [c.strip() for c in line.split('|') if c.strip()]
            tag = 'th' if i == 0 else 'td'
            html_table += '<tr>' + ''.join(f'<{tag} class="px-4 py-3 text-left text-sm">{c}</{tag}>' for c in cells) + '</tr>\n'
        
        html_table += '</table>'
        return html_table
    
    # Match tables
    html = re.sub(r'(\|[^\n]+\|\n)+(\|[-]+\|\n)?(\|[^\n]+\|\n)+', convert_table, html, flags=re.MULTILINE)
    
    # Unordered lists
    def convert_list(match):
        items = match.group(0).strip().split('\n')
        html_list = '<ul class="list-disc list-inside mb-4 space-y-2">\n'
        for item in items:
            text = re.sub(r'^- ', '', item)
            html_list += f'<li>{text}</li>\n'
        html_list += '</ul>'
        return html_list
    
    html = re.sub(r'(^- .+\n)+', convert_list, html, flags=re.MULTILINE)
    
    # Ordered lists
    def convert_ordered_list(match):
        items = match.group(0).strip().split('\n')
        html_list = '<ol class="list-decimal list-inside mb-4 space-y-2">\n'
        for item in items:
            text = re.sub(r'^\d+\. ', '', item)
            html_list += f'<li>{text}</li>\n'
        html_list += '</ol>'
        return html_list
    
    html = re.sub(r'(^\d+\. .+\n)+', convert_ordered_list, html, flags=re.MULTILINE)
    
    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener" class="text-blue-600 hover:underline">\1</a>', html)
    
    # Paragraphs (must be last)
    paragraphs = []
    lines = html.split('\n\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Don't wrap if already a block element
        if re.match(r'^<(h[1-6]|table|ul|ol|blockquote|hr|div|figure)', line):
            paragraphs.append(line)
        else:
            paragraphs.append(f'<p>{line}</p>')
    
    return '\n'.join(paragraphs)


def extract_faq_section(content):
    """Extract FAQ section and convert to HTML."""
    # Find FAQ section
    faq_match = re.search(r'## 常見問題 FAQ(.*?)(?=## 參考資料|$)', content, re.DOTALL)
    if not faq_match:
        return '', ''
    
    faq_text = faq_match.group(1).strip()
    
    # Extract Q&A pairs
    qa_pairs = re.findall(r'### (Q\d+: .*?)\n\n(.*?)(?=\n### Q\d+:|$)', faq_text, re.DOTALL)
    
    if not qa_pairs:
        return '', ''
    
    # Build FAQ HTML
    faq_html = '''
    <section class="mt-12 pt-8 border-t border-gray-200">
        <h2 class="text-2xl font-bold text-[#0F172A] mb-6">常見問題 FAQ</h2>
        <div class="space-y-6">
'''
    
    for q, a in qa_pairs:
        answer_html = markdown_to_html(a.strip())
        faq_html += f'''
            <div class="bg-gray-50 rounded-xl p-6">
                <h3 class="text-lg font-bold text-[#1e3a8a] mb-3">{q}</h3>
                <div class="text-gray-600 leading-relaxed">
                    {answer_html}
                </div>
            </div>
'''
    
    faq_html += '        </div>\n    </section>'
    
    # Build FAQ JSON-LD
    faq_jsonld = '''<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
'''
    
    entities = []
    for q, a in qa_pairs:
        q_text = re.sub(r'^Q\d+: ', '', q).strip()
        a_text = re.sub(r'<[^>]+>', '', a).strip().replace('\n', ' ')
        entities.append(f'''        {{
            "@type": "Question",
            "name": "{q_text}",
            "acceptedAnswer": {{
                "@type": "Answer",
                "text": "{a_text}"
            }}
        }}''')
    
    faq_jsonld += ',\n'.join(entities)
    faq_jsonld += '''
    ]
}
</script>'''
    
    return faq_html, faq_jsonld


def extract_references_section(content):
    """Extract References section and convert to HTML."""
    ref_match = re.search(r'## 參考資料 References(.*?)(?=---\n\*\*免責|$)', content, re.DOTALL)
    if not ref_match:
        return ''
    
    ref_text = ref_match.group(1).strip()
    
    # Extract reference links
    refs = re.findall(r'- \[([^\]]+)\]\(([^)]+)\)', ref_text)
    
    if not refs:
        return ''
    
    ref_html = '''
    <section class="mt-12 pt-8 border-t border-gray-200">
        <h2 class="text-2xl font-bold text-[#0F172A] mb-6">參考資料 References</h2>
        <ul class="space-y-3">
'''
    
    for title, url in refs:
        ref_html += f'''            <li class="flex items-start gap-2">
                <i class="fas fa-external-link-alt text-gray-400 mt-1 text-sm"></i>
                <a href="{url}" target="_blank" rel="noopener" class="text-blue-600 hover:underline">{title}</a>
            </li>
'''
    
    ref_html += '        </ul>\n    </section>'
    
    return ref_html


def convert_md_to_html(md_path, output_path, template_path=None):
    """Convert a Markdown file to HTML."""
    
    # Parse Markdown
    metadata, body = parse_markdown(md_path)
    
    if not metadata:
        print(f"❌ Failed to parse YAML front matter: {md_path}")
        return False
    
    # Read template
    template_path = template_path or TEMPLATE_FILE
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Determine if English version
    is_english = metadata.get('lang', 'zh-TW') == 'en'
    
    # Extract FAQ and References
    faq_html, faq_jsonld = extract_faq_section(body)
    ref_html = extract_references_section(body)
    
    # Remove FAQ and References from body for main content
    main_content = re.sub(r'## 常見問題 FAQ.*$', '', body, flags=re.DOTALL)
    main_content = re.sub(r'## 參考資料 References.*$', '', main_content, flags=re.DOTALL)
    main_content = main_content.strip()
    main_content = re.sub(r'---\n\*\*免責聲明：.*$', '', main_content, flags=re.DOTALL)
    main_content = main_content.strip()
    
    # Convert to HTML
    content_html = markdown_to_html(main_content)
    
    # Build disclaimer
    disclaimer = '''
    <div class="mt-8 p-6 bg-gray-100 rounded-xl text-sm text-gray-600">
        <p><strong>免責聲明：</strong>本文僅供參考，不構成投資建議。海外房地產投資涉及匯率風險、政治風險、法律風險等，投資前請諮詢專業顧問。鼎曜國際顧問不對投資結果負責。</p>
    </div>
'''
    
    # Prepare replacements
    category_key = CATEGORIES.get(metadata.get('category', '投資'), 'investment')
    category_label = CATEGORY_LABELS.get(metadata.get('category', '投資'), '投資')
    
    replacements = {
        '{{ARTICLE_TITLE}}': metadata.get('title', ''),
        '{{ARTICLE_DESCRIPTION}}': metadata.get('description', ''),
        '{{ARTICLE_KEYWORDS}}': metadata.get('keywords', ''),
        '{{ARTICLE_SLUG}}': metadata.get('slug', ''),
        '{{ARTICLE_DATE}}': str(metadata.get('date', '')),
        '{{ARTICLE_CATEGORY}}': category_key,
        '{{ARTICLE_CATEGORY_LABEL}}': category_label,
        '{{ARTICLE_IMAGE}}': f"{metadata.get('featured_image', '')}.jpg",
        '{{ARTICLE_IMAGE_BASE}}': metadata.get('featured_image', ''),
        '{{ARTICLE_HERO_BG}}': f"{metadata.get('featured_image', '')}.jpg",
        '{{ARTICLE_IMAGE_CAPTION}}': metadata.get('title', ''),
        '{{ARTICLE_CONTENT}}': content_html,
        '{{FAQ_SECTION}}': faq_html,
        '{{FAQ_SCHEMA}}': faq_jsonld,
        '{{REFERENCES_SECTION}}': ref_html,
        '{{CTA_TITLE}}': '準備好在開普敦開啟新生活？',
        '{{CTA_DESCRIPTION}}': '無論是置產投資、子女教育、退休規劃，我們都能提供專業建議。',
        '{{RELATED_ARTICLES}}': '<p class="text-gray-500 col-span-3">相關文章載入中...</p>',
    }
    
    # Replace placeholders
    html = template
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)
    
    # Clean up unused placeholders
    html = re.sub(r'\{\{[A-Z_]+\}\}', '', html)
    
    # Update language tag for English
    if is_english:
        html = html.replace('lang="zh-TW"', 'lang="en"')
        html = html.replace('hreflang="zh-TW"', 'hreflang="en"')
        # Swap language links
        html = re.sub(r'href="{{ARTICLE_SLUG}}-en\.html"', f'href="{metadata.get("slug", "")}.html"', html)
        html = html.replace('>EN</a>', '>TW</a>')
        html = html.replace('>TW</span>', '>EN</span>')
    
    # Write output
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Converted: {md_path.name} → {Path(output_path).name}")
    return True


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    action = sys.argv[1]
    
    if action == '--input' and len(sys.argv) >= 4:
        input_path = Path(sys.argv[2])
        output_path = sys.argv[3]
        convert_md_to_html(input_path, output_path)
    
    elif action == '--batch' and len(sys.argv) >= 4:
        input_dir = Path(sys.argv[2])
        output_dir = Path(sys.argv[3])
        
        for md_file in input_dir.glob('*.md'):
            # Determine output filename
            if '-zh.md' in md_file.name:
                output_name = md_file.name.replace('-zh.md', '.html').replace(md_file.name[:11], '')
                output_name = md_file.name[11:].replace('-zh.md', '.html')
            elif '-en.md' in md_file.name:
                output_name = md_file.name[11:].replace('-en.md', '-en.html')
            else:
                continue
            
            convert_md_to_html(md_file, output_dir / output_name)
    
    else:
        print(__doc__)


if __name__ == '__main__':
    main()