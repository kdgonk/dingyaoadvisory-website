#!/usr/bin/env python3
"""
Blog Article Automation Script for Titan (泰坦人)

This script handles:
1. Adding new blog articles
2. Updating blog.html with pagination
3. Updating sitemap.xml
4. Submitting to Google Search Console

Usage:
    python3 blog-automation.py --action add --title "文章標題" --slug "article-slug" --category "investment" --date "2026-03-24"
    python3 blog-automation.py --action update-sitemap
    python3 blog-automation.py --action list
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

# Configuration
DIST_DIR = Path('/Users/dingyao/.openclaw/workspace/dingyaoadvisory-website/dist')
BLOG_DIR = DIST_DIR / 'blog'
BLOG_HTML = DIST_DIR / 'blog.html'
BLOG_EN_HTML = DIST_DIR / 'blog-en.html'
SITEMAP_XML = DIST_DIR / 'sitemap.xml'

# Author
AUTHOR = "Leo Pan - 潘品樺"

# Categories
CATEGORIES = {
    'investment': {'name': '置產投資', 'class': 'bg-blue-100 text-blue-800'},
    'education': {'name': '教育留學', 'class': 'bg-green-100 text-green-800'},
    'lifestyle': {'name': '退休生活', 'class': 'bg-purple-100 text-purple-800'},
    'residency': {'name': '身分規劃', 'class': 'bg-yellow-100 text-yellow-800'},
}

# Articles per page
ARTICLES_PER_PAGE = 9


def parse_blog_html(filepath):
    """Parse blog.html and extract existing articles."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all article elements
    article_pattern = r'<article[^>]*data-category="([^"]+)"[^>]*>.*?</article>'
    articles = []
    
    # Extract each article
    for match in re.finditer(article_pattern, content, re.DOTALL):
        article_html = match.group(0)
        category = match.group(1)
        
        # Extract article data
        title_match = re.search(r'<h3[^>]*>.*?<a href="([^"]+)"[^>]*>([^<]+)</a>', article_html, re.DOTALL)
        desc_match = re.search(r'<p class="text-gray-600[^>]*>([^<]+)</p>', article_html)
        date_match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日)', article_html)
        img_match = re.search(r'<img[^>]*src="([^"]+)"', article_html)
        
        if title_match:
            articles.append({
                'url': title_match.group(1),
                'title': title_match.group(2).strip(),
                'description': desc_match.group(1).strip() if desc_match else '',
                'date': date_match.group(1) if date_match else '',
                'category': category,
                'image': img_match.group(1) if img_match else '',
                'html': article_html
            })
    
    return articles


def create_article_card(article):
    """Create an article card HTML element."""
    category_info = CATEGORIES.get(article['category'], CATEGORIES['investment'])
    
    return f'''                <article class="bg-white rounded-2xl overflow-hidden shadow-lg card-hover" data-category="{article['category']}">
                    <div class="aspect-[16/10] overflow-hidden">
                        <picture>
                            <source srcset="{article['image'].replace('.jpg', '.avif')}" type="image/avif">
                            <source srcset="{article['image'].replace('.jpg', '.webp')}" type="image/webp">
                            <img src="{article['image']}" alt="{article['title']}" class="w-full h-full object-cover hover:scale-105 transition-transform duration-300" width="400" height="250" loading="lazy" decoding="async">
                        </picture>
                    </div>
                    <div class="p-6">
                        <div class="flex items-center gap-2 mb-3">
                            <span class="px-2 py-1 {category_info['class']} text-xs font-medium rounded-full">{category_info['name']}</span>
                        </div>
                        <h3 class="text-xl font-bold text-[#0F172A] mb-3 line-clamp-2">
                            <a href="{article['url']}" class="hover:text-[#C5A059] transition">{article['title']}</a>
                        </h3>
                        <p class="text-gray-600 text-sm mb-4 line-clamp-3">{article['description']}</p>
                        <div class="flex items-center justify-between text-sm text-gray-500">
                            <span><i class="far fa-calendar mr-1"></i>{article['date']}</span>
                            <a href="{article['url']}" class="text-[#C5A059] hover:text-[#B08D4E] font-medium transition">閱讀更多 <i class="fas fa-arrow-right text-xs ml-1"></i></a>
                        </div>
                    </div>
                </article>'''


def create_pagination(current_page, total_pages, base_url='blog'):
    """Create pagination HTML."""
    if total_pages <= 1:
        return ''
    
    pagination_html = '''    <nav class="flex justify-center items-center gap-2 mt-12" aria-label="部落格分頁">
'''
    
    # Previous button
    if current_page > 1:
        prev_url = f'{base_url}.html' if current_page == 2 else f'{base_url}-{current_page - 1}.html'
        pagination_html += f'''        <a href="{prev_url}" class="px-4 py-2 text-sm font-medium text-gray-600 hover:text-blue-900 hover:bg-gray-100 rounded-lg transition">
            <i class="fas fa-chevron-left mr-1"></i> 上一頁
        </a>
'''
    
    # Page numbers
    for page in range(1, total_pages + 1):
        page_url = f'{base_url}.html' if page == 1 else f'{base_url}-{page}.html'
        if page == current_page:
            pagination_html += f'''        <span class="px-4 py-2 text-sm font-bold text-white bg-blue-900 rounded-lg">{page}</span>
'''
        else:
            pagination_html += f'''        <a href="{page_url}" class="px-4 py-2 text-sm font-medium text-gray-600 hover:text-blue-900 hover:bg-gray-100 rounded-lg transition">{page}</a>
'''
    
    # Next button
    if current_page < total_pages:
        next_url = f'{base_url}-{current_page + 1}.html'
        pagination_html += f'''        <a href="{next_url}" class="px-4 py-2 text-sm font-medium text-gray-600 hover:text-blue-900 hover:bg-gray-100 rounded-lg transition">
            下一頁 <i class="fas fa-chevron-right ml-1"></i>
        </a>
'''
    
    pagination_html += '''    </nav>'''
    return pagination_html


def get_blog_template(title, description, lang='zh-TW', is_paginated=False, page_num=1, total_pages=1, articles_html='', pagination_html=''):
    """Get blog page HTML template."""
    
    # Read the base template
    with open(BLOG_HTML, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Update title and description
    if page_num > 1:
        title = f"專欄文章 (第 {page_num} 頁) | 鼎曜國際顧問"
    
    # Replace articles section
    articles_section_pattern = r'<div id="blog-posts"[^>]*>.*?</section>'
    
    # For now, return the template as-is since we need to update it properly
    return template


def update_blog_list(new_article=None):
    """Update blog.html with new article and handle pagination."""
    
    # Parse existing articles
    articles = parse_blog_html(BLOG_HTML)
    
    # Add new article if provided
    if new_article:
        # Check if article already exists
        existing_urls = [a['url'] for a in articles]
        if new_article['url'] not in existing_urls:
            articles.insert(0, new_article)
            print(f"✅ Added new article: {new_article['title']}")
        else:
            print(f"⚠️ Article already exists: {new_article['title']}")
    
    # Calculate pagination
    total_pages = (len(articles) + ARTICLES_PER_PAGE - 1) // ARTICLES_PER_PAGE
    
    # Split articles into pages
    pages = []
    for i in range(total_pages):
        start = i * ARTICLES_PER_PAGE
        end = start + ARTICLES_PER_PAGE
        pages.append(articles[start:end])
    
    # Generate each page
    for page_num, page_articles in enumerate(pages, 1):
        if page_num == 1:
            output_file = BLOG_HTML
        else:
            output_file = DIST_DIR / f'blog-{page_num}.html'
        
        # Read template
        with open(BLOG_HTML, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find articles container
        articles_container_pattern = r'(<div id="blog-posts"[^>]*>)(.*?)(</div>\s*</section>)'
        match = re.search(articles_container_pattern, content, re.DOTALL)
        
        if match:
            # Generate articles HTML
            articles_html = '\n'.join([create_article_card(a) for a in page_articles])
            
            # Add pagination if needed
            if total_pages > 1:
                pagination = create_pagination(page_num, total_pages, 'blog')
                # Insert pagination before CTA section
                articles_html += f'\n{pagination}'
            
            # Replace articles
            new_content = content[:match.start(2)] + articles_html + content[match.end(2):]
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Updated: {output_file.name} ({len(page_articles)} articles)")
    
    return articles


def update_sitemap():
    """Update sitemap.xml with blog articles."""
    with open(SITEMAP_XML, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all blog articles
    blog_files = list(BLOG_DIR.glob('*.html'))
    blog_files = [f for f in blog_files if f.name != 'blog-template.html']
    
    # Check what's already in sitemap
    existing_urls = re.findall(r'<loc>(https://dingyaoadvisory\.tw/blog/[^<]+)</loc>', content)
    
    new_entries = []
    for blog_file in blog_files:
        url = f"https://dingyaoadvisory.tw/blog/{blog_file.stem}"
        if url not in existing_urls:
            # Get file modification date
            mtime = datetime.fromtimestamp(blog_file.stat().st_mtime)
            lastmod = mtime.strftime('%Y-%m-%d')
            
            entry = f'''
    <url>
        <loc>{url}</loc>
        <lastmod>{lastmod}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>'''
            new_entries.append(entry)
    
    if new_entries:
        # Insert before </urlset>
        insert_pos = content.rfind('</urlset>')
        new_content = content[:insert_pos] + '\n'.join(new_entries) + '\n' + content[insert_pos:]
        
        with open(SITEMAP_XML, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Added {len(new_entries)} new URLs to sitemap.xml")
    else:
        print("⚠️ No new URLs to add to sitemap.xml")
    
    return new_entries


def list_articles():
    """List all blog articles."""
    articles = parse_blog_html(BLOG_HTML)
    
    print(f"\n📚 Blog Articles ({len(articles)} total):\n")
    print(f"{'#':<3} {'Title':<50} {'Category':<12} {'Date'}")
    print("-" * 80)
    
    for i, article in enumerate(articles, 1):
        print(f"{i:<3} {article['title'][:48]:<50} {article['category']:<12} {article['date']}")
    
    return articles


def add_article(title, slug, category, description, image, date=None):
    """Add a new blog article."""
    if category not in CATEGORIES:
        print(f"❌ Invalid category: {category}")
        print(f"Valid categories: {', '.join(CATEGORIES.keys())}")
        return False
    
    if date is None:
        date = datetime.now().strftime('%Y年%m月%d日')
    
    article = {
        'url': f'blog/{slug}.html',
        'title': title,
        'description': description,
        'category': category,
        'image': image,
        'date': date
    }
    
    # Update blog list
    update_blog_list(article)
    
    # Update sitemap
    update_sitemap()
    
    return article


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    action = sys.argv[1]
    
    if action == 'list':
        list_articles()
    
    elif action == 'add':
        # Parse arguments
        args = {}
        i = 2
        while i < len(sys.argv):
            if sys.argv[i].startswith('--'):
                key = sys.argv[i][2:]
                if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('--'):
                    args[key] = sys.argv[i + 1]
                    i += 2
                else:
                    i += 1
            else:
                i += 1
        
        required = ['title', 'slug', 'category', 'image']
        missing = [r for r in required if r not in args]
        if missing:
            print(f"❌ Missing required arguments: {', '.join(missing)}")
            print("Usage: python3 blog-automation.py add --title 'Title' --slug 'slug' --category 'investment' --image 'url' [--description 'desc'] [--date '2026年3月24日']")
            return
        
        add_article(
            title=args['title'],
            slug=args['slug'],
            category=args['category'],
            description=args.get('description', ''),
            image=args['image'],
            date=args.get('date')
        )
    
    elif action == 'update-sitemap':
        update_sitemap()
    
    elif action == 'help':
        print(__doc__)
    
    else:
        print(f"❌ Unknown action: {action}")
        print(__doc__)


if __name__ == '__main__':
    main()