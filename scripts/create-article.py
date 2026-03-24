#!/usr/bin/env python3
"""
Blog Article Generator for Titan (泰坦人)
Creates a new blog article from template.

Usage:
    python3 create-article.py --slug "article-slug" --title "Title" --category "investment" --description "Description" --image "url" --date "2026年3月24日"
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path

# Configuration
DIST_DIR = Path('/Users/dingyao/.openclaw/workspace/dingyaoadvisory-website/dist')
BLOG_DIR = DIST_DIR / 'blog'
TEMPLATE_FILE = BLOG_DIR / 'blog-template.html'

# Categories
CATEGORIES = {
    'investment': '置產投資',
    'education': '教育留學',
    'lifestyle': '退休生活',
    'residency': '身分規劃',
}

# Author
AUTHOR = "Leo Pan - 潘品樺"


def get_article_template():
    """Read the blog template."""
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def create_article_html(slug, title, title_en, category, description, description_en, image, date, date_en, content, content_en=None):
    """Create a new blog article HTML file."""
    
    template = get_article_template()
    
    # Format date
    if isinstance(date, str) and '年' in date:
        date_cn = date
        date_iso = datetime.strptime(date.replace('年', '-').replace('月', '-').replace('日', ''), '%Y-%m-%d').strftime('%Y-%m-%d')
    else:
        date_cn = date
        date_iso = date
    
    # Get category name
    category_name = CATEGORIES.get(category, category)
    
    # Replace placeholders in template
    replacements = {
        '{{TITLE}}': title,
        '{{TITLE_EN}}': title_en or title,
        '{{DESCRIPTION}}': description,
        '{{DESCRIPTION_EN}}': description_en or description,
        '{{CATEGORY}}': category,
        '{{CATEGORY_NAME}}': category_name,
        '{{IMAGE}}': image,
        '{{IMAGE_ALT}}': title,
        '{{DATE}}': date_cn,
        '{{DATE_EN}}': date_en or date_cn,
        '{{DATE_ISO}}': date_iso,
        '{{AUTHOR}}': AUTHOR,
        '{{SLUG}}': slug,
        '{{CONTENT}}': content,
    }
    
    # If content_en is provided, replace English content placeholder
    if content_en:
        replacements['{{CONTENT_EN}}'] = content_en
    
    # Replace all placeholders
    html = template
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, str(value))
    
    # Clean up unused placeholders
    html = re.sub(r'\{\{[A-Z_]+\}\}', '', html)
    
    return html


def create_seo_data(title, title_en, description, description_en, slug, image, date_iso, category):
    """Create SEO metadata for the article."""
    
    category_name = CATEGORIES.get(category, category)
    
    # JSON-LD for Article
    article_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "image": image,
        "datePublished": date_iso,
        "dateModified": date_iso,
        "author": {
            "@type": "Person",
            "name": AUTHOR
        },
        "publisher": {
            "@type": "Organization",
            "name": "鼎曜國際顧問",
            "logo": {
                "@type": "ImageObject",
                "url": "https://assets.dingyaoadvisory.tw/dingyao%20logo.png"
            }
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"https://dingyaoadvisory.tw/blog/{slug}"
        }
    }
    
    # JSON-LD for Breadcrumb
    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "首頁",
                "item": "https://dingyaoadvisory.tw"
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "專欄",
                "item": "https://dingyaoadvisory.tw/blog"
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": category_name
            },
            {
                "@type": "ListItem",
                "position": 4,
                "name": title
            }
        ]
    }
    
    return {
        'article_schema': article_schema,
        'breadcrumb_schema': breadcrumb_schema
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    # Parse arguments
    args = {}
    i = 1
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
    
    # Required arguments
    required = ['slug', 'title', 'category', 'description', 'image', 'date']
    missing = [r for r in required if r not in args]
    if missing:
        print(f"❌ Missing required arguments: {', '.join(missing)}")
        print("\nUsage:")
        print("python3 create-article.py \\")
        print("  --slug 'article-slug' \\")
        print("  --title 'Article Title' \\")
        print("  --title_en 'English Title' \\")
        print("  --category 'investment' \\")
        print("  --description 'Article description' \\")
        print("  --description_en 'English description' \\")
        print("  --image 'https://assets.dingyaoadvisory.tw/blog-image.jpg' \\")
        print("  --date '2026年3月24日'")
        return
    
    # Validate category
    if args['category'] not in CATEGORIES:
        print(f"❌ Invalid category: {args['category']}")
        print(f"Valid categories: {', '.join(CATEGORIES.keys())}")
        return
    
    print(f"📝 Creating article: {args['title']}")
    print(f"   Slug: {args['slug']}")
    print(f"   Category: {CATEGORIES[args['category']]}")
    
    # This is a placeholder - the actual article creation would need more content
    print("\n✅ Article template ready!")
    print("   Please use the full blog-automation.py script to add the article.")


if __name__ == '__main__':
    main()