#!/usr/bin/env python3
"""
批量修正 dingyaoadvisory.tw 網站的 Navigation 和 Footer
使用 blog.html 作為標準版型
"""

import os
import re
import sys

DIST_DIR = "/Users/dingyao/.openclaw/workspace/dingyaoadvisory-website/dist"

# Standard Navigation template (TW version, will be adjusted for EN and subdirectories)
NAV_TEMPLATE_TW = '''<!-- Navigation -->
    <div class="fixed w-full z-50 top-4 md:top-6 px-4 pointer-events-none">
        <nav class="max-w-7xl mx-auto bg-white/95 backdrop-blur-xl border border-white/40 shadow-2xl rounded-3xl px-6 py-3 transition-all duration-300 relative pointer-events-auto">
            <div class="flex justify-between items-center">
                <div class="flex items-center gap-4 cursor-pointer group" onclick="location.href='{index_path}'">
                    <div class="relative group-hover:scale-105 transition-transform duration-300">
                        <div class="text-3xl font-bold font-logo tracking-tighter leading-none select-none">
                            <span class="text-[#0F172A]">D</span><span class="text-[#C5A059]">Y</span><span class="text-[#0F172A]">A</span>
                        </div>
                        <div class="absolute -top-1 -right-1 w-2 h-2 bg-green-500 rounded-full border border-white"></div>
                    </div>
                    <div class="hidden lg:flex items-center gap-3">
                        <div class="h-8 w-px bg-gray-200 mx-1"></div>
                        <div class="flex flex-col justify-center">
                            <span class="text-[0.65rem] font-bold text-[#0F172A] tracking-[0.2em] uppercase leading-tight font-logo">DING YAO</span>
                            <span class="text-[0.55rem] text-gray-400 font-medium tracking-[0.1em] uppercase leading-tight">ADVISORY</span>
                        </div>
                        <span class="ml-2 text-[0.5rem] bg-[#0F172A] text-white px-1.5 py-0.5 rounded border border-gray-700 font-bold tracking-widest uppercase opacity-80">APAC HUB</span>
                    </div>
                </div>
                <div class="hidden md:flex items-center space-x-1">
                    <a class="px-4 py-2 text-sm font-medium {partners_active} rounded-full transition" href="{path_prefix}partners.html">戰略夥伴</a>
                    <a class="px-4 py-2 text-sm font-medium {platform_active} rounded-full transition" href="{path_prefix}platform.html">數位服務</a>
                    <div class="relative group dropdown-container">
                        <button class="px-4 py-2 text-sm font-medium text-gray-600 hover:text-blue-900 hover:bg-gray-100/50 rounded-full transition flex items-center focus:outline-none">
                            美好生活 <i class="fas fa-chevron-down ml-1 text-xs opacity-50 transition-transform duration-300 group-hover:-rotate-180"></i>
                        </button>
                        <div class="absolute top-full left-0 mt-2 w-48 bg-white/95 backdrop-blur-md border border-white/50 rounded-2xl shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 transform translate-y-2 overflow-hidden p-2">
                            <a class="block px-4 py-2 text-sm text-gray-600 hover:bg-blue-50 hover:text-blue-900 rounded-xl transition flex items-center" href="{path_prefix}education.html"><i class="fas fa-graduation-cap w-6 text-center mr-2 text-yellow-500"></i> 教育留學</a>
                            <a class="block px-4 py-2 text-sm text-gray-600 hover:bg-blue-50 hover:text-blue-900 rounded-xl transition flex items-center" href="{path_prefix}retirement.html"><i class="fas fa-wine-glass-alt w-6 text-center mr-2 text-red-500"></i> 退休生活</a>
                            <a class="block px-4 py-2 text-sm text-gray-600 hover:bg-blue-50 hover:text-blue-900 rounded-xl transition flex items-center" href="{path_prefix}residency.html"><i class="fas fa-passport w-6 text-center mr-2 text-blue-500"></i> 身分規劃</a>
                        </div>
                    </div>
                    <a class="px-4 py-2 text-sm font-medium {assets_active} rounded-full transition" href="{path_prefix}assets.html">精選資產</a>
                    <a class="px-4 py-2 text-sm font-medium {blog_active} rounded-full transition" href="{path_prefix}blog.html">專欄</a>
                </div>
                <div class="hidden md:flex items-center gap-3">
                    <div class="flex items-center text-xs font-bold text-gray-400">
                        <a class="hover:text-blue-900 transition" href="{lang_switch_path}">EN</a>
                        <span class="mx-2">/</span>
                        <span class="text-blue-900 cursor-default">TW</span>
                    </div>
                    <a class="bg-blue-900 text-white hover:bg-blue-800 px-6 py-2 rounded-full text-xs font-bold shadow-lg shadow-blue-900/20 transform hover:-translate-y-0.5 transition whitespace-nowrap" href="{path_prefix}index.html#contact">預約諮詢</a>
                </div>
                <div class="md:hidden flex items-center gap-4">
                    <a class="text-sm font-bold text-gray-700 bg-white border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-100 shadow-sm relative z-50 pointer-events-auto cursor-pointer block" href="{lang_switch_path}">EN</a>
                    <button class="text-gray-700 bg-white border border-gray-300 focus:outline-none p-2 ml-2 relative z-50 pointer-events-auto cursor-pointer flex items-center justify-center rounded-lg hover:bg-gray-100 shadow-sm" onclick="toggleMobileMenu()" type="button">
                        <i class="fas fa-bars text-xl"></i>
                    </button>
                </div>
            </div>
            <!-- Mobile Menu -->
            <div class="hidden md:hidden border-t border-gray-100 mt-3 pt-2 space-y-1" id="mobile-menu">
                <a class="block px-4 py-3 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-xl" href="{path_prefix}partners.html">戰略夥伴</a>
                <a class="block px-4 py-3 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-xl" href="{path_prefix}platform.html">數位服務</a>
                <div class="pl-4 border-l-2 border-gray-100 ml-4 my-2">
                    <p class="text-xs text-gray-400 uppercase tracking-widest mb-2 pl-2">美好生活</p>
                    <a class="block px-4 py-2 text-sm text-gray-600 hover:text-blue-900" href="{path_prefix}education.html">教育留學</a>
                    <a class="block px-4 py-2 text-sm text-gray-600 hover:text-blue-900" href="{path_prefix}retirement.html">退休生活</a>
                    <a class="block px-4 py-2 text-sm text-gray-600 hover:text-blue-900" href="{path_prefix}residency.html">身分規劃</a>
                </div>
                <a class="block px-4 py-3 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-xl" href="{path_prefix}assets.html">精選資產</a>
                <a class="block px-4 py-3 text-sm font-medium {blog_active_mobile} rounded-xl" href="{path_prefix}blog.html">專欄</a>
                <a class="block px-4 py-3 text-sm font-bold text-center text-white bg-blue-900 rounded-xl mt-4 shadow-lg" href="{path_prefix}index.html#contact" onclick="toggleMobileMenu()">立即預約諮詢</a>
            </div>
        </nav>
    </div>
'''

# Standard Footer template
FOOTER_TEMPLATE = '''<!-- Footer -->
    <footer class="bg-[#0f172a] text-gray-400 py-16 border-t border-gray-800 text-sm font-light">
        <div class="max-w-7xl mx-auto px-6">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-12">
                <div class="space-y-4">
                    <div class="flex items-center gap-2">
                        <span class="text-white font-bold text-2xl tracking-tight uppercase font-logo">D<span class="text-[#C5A059]">Y</span>A</span>
                        <div class="h-4 w-px bg-gray-600"></div>
                        <span class="text-gray-300 font-medium text-xs tracking-widest uppercase">DINGYAO ADVISORY</span>
                    </div>
                    <p class="text-gray-500 leading-relaxed text-xs"><strong>亞太區獨家數位行銷中心</strong><br/>我們致力於消除跨境投資的資訊落差。透過數位託管技術，連結台灣資金與南非頂級資產。</p>
                    <div class="flex flex-wrap gap-3 pt-2">
                        <a class="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center hover:bg-yellow-500 hover:text-blue-900 transition" href="https://www.facebook.com/DingYaoAdvisory/" target="_blank" rel="noopener noreferrer" aria-label="Facebook"><i class="fab fa-facebook-f"></i></a>
                        <a class="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center hover:bg-yellow-500 hover:text-blue-900 transition" href="https://www.instagram.com/dingyaoadvisory" target="_blank" rel="noopener noreferrer" aria-label="Instagram"><i class="fab fa-instagram"></i></a>
                        <a class="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center hover:bg-yellow-500 hover:text-blue-900 transition" href="https://x.com/dingyaoadvisory" target="_blank" rel="noopener noreferrer" aria-label="X (Twitter)"><i class="fab fa-x-twitter"></i></a>
                        <a class="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center hover:bg-yellow-500 hover:text-blue-900 transition" href="https://www.linkedin.com/company/dingyaoadvisory/" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn"><i class="fab fa-linkedin-in"></i></a>
                        <a class="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center hover:bg-yellow-500 hover:text-blue-900 transition" href="https://www.threads.net/@dingyaoadvisory" target="_blank" rel="noopener noreferrer" aria-label="Threads"><i class="fab fa-threads"></i></a>
                        <a class="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center hover:bg-yellow-500 hover:text-blue-900 transition" href="https://www.youtube.com/@dingyaoadvisory" target="_blank" rel="noopener noreferrer" aria-label="YouTube"><i class="fab fa-youtube"></i></a>
                    </div>
                </div>
                <div>
                    <h4 class="text-white font-bold mb-6 uppercase text-xs tracking-widest border-b border-gray-800 pb-2 inline-block">戰略生態系連結</h4>
                    <ul class="space-y-3 text-xs">
                        <li><a class="hover:text-yellow-500 transition flex items-center group" href="https://crestlineadvisory.co.za" target="_blank" rel="noopener noreferrer"><i class="fas fa-external-link-alt mr-2 text-gray-600 group-hover:text-yellow-500"></i>Crestline Advisory (執行端)</a></li>
                        <li><a class="hover:text-yellow-500 transition flex items-center group" href="https://canvascrest.co.za" target="_blank" rel="noopener noreferrer"><i class="fas fa-external-link-alt mr-2 text-gray-600 group-hover:text-yellow-500"></i>CanvasCrest Properties (開發端)</a></li>
                        <li><a class="hover:text-yellow-500 transition flex items-center group" href="https://www.standardbank.co.za" target="_blank" rel="noopener noreferrer"><i class="fas fa-university mr-2 text-gray-600 group-hover:text-yellow-500"></i>Standard Bank (資金託管)</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="text-white font-bold mb-6 uppercase text-xs tracking-widest border-b border-gray-800 pb-2 inline-block">核心服務</h4>
                    <ul class="space-y-3 text-xs">
                        <li><a class="hover:text-yellow-500 transition" href="{path_prefix}assets.html">海外置產顧問</a></li>
                        <li><a class="hover:text-yellow-500 transition" href="{path_prefix}education.html">頂級留學規劃</a></li>
                        <li><a class="hover:text-yellow-500 transition" href="{path_prefix}retirement.html">退休移居方案</a></li>
                        <li><a class="hover:text-yellow-500 transition" href="{path_prefix}residency.html">永久居留權 (PR)</a></li>
                        <li><a class="hover:text-yellow-500 transition" href="{path_prefix}platform.html">數位資產平台</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="text-white font-bold mb-6 uppercase text-xs tracking-widest border-b border-gray-800 pb-2 inline-block">合規與聯繫</h4>
                    <ul class="space-y-3 text-xs">
                        <li><a class="hover:text-white transition" href="{path_prefix}privacy.html">隱私權政策 (Privacy)</a></li>
                        <li><a class="hover:text-white transition" href="{path_prefix}terms.html">服務條款 (Terms)</a></li>
                        <li class="pt-4 text-gray-500"><i class="fas fa-map-marker-alt mr-2"></i> 台中市西屯區 (亞太總部)</li>
                        <li class="text-gray-500"><i class="fas fa-envelope mr-2"></i> <a class="hover:text-white transition" href="mailto:info@dingyaoadvisory.tw">info@dingyaoadvisory.tw</a></li>
                    </ul>
                </div>
            </div>
            <div class="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center text-xs text-gray-600">
                <div class="mb-4 md:mb-0">
                    © <span id="copyright-year">2025-2026</span> <a class="font-bold hover:text-yellow-500 transition duration-300" href="{path_prefix}index.html">鼎曜國際顧問有限公司</a> All rights reserved. | Taichung, Taiwan
                </div>
                <div class="flex space-x-6">
                    <span>Designed for Global Investors</span>
                </div>
            </div>
        </div>
    </footer>

    <script>
        function toggleMobileMenu() {{
            const menu = document.getElementById('mobile-menu');
            menu.classList.toggle('hidden');
        }}
    </script>
'''

def get_page_type(filename):
    """Determine which nav item should be active based on filename"""
    basename = os.path.basename(filename)
    
    if 'partners' in basename:
        return 'partners'
    elif 'platform' in basename:
        return 'platform'
    elif 'assets' in basename:
        return 'assets'
    elif 'blog' in basename:
        return 'blog'
    elif 'education' in basename:
        return 'education'
    elif 'retirement' in basename:
        return 'retirement'
    elif 'residency' in basename:
        return 'residency'
    elif 'index' in basename:
        return 'index'
    elif 'project' in basename:
        return 'assets'  # Project pages are under assets
    else:
        return 'other'

def is_english(filename):
    """Check if the file is English version"""
    basename = os.path.basename(filename)
    return '-en' in basename or basename.endswith('-en.html')

def is_in_blog_subdir(filename):
    """Check if file is in blog/ subdirectory"""
    return '/blog/' in filename

def generate_nav(filename):
    """Generate navigation HTML for a specific file"""
    page_type = get_page_type(filename)
    is_en = is_english(filename)
    is_blog_subdir = is_in_blog_subdir(filename)
    
    # Determine path prefix
    if is_blog_subdir:
        path_prefix = '../'
    else:
        path_prefix = ''
    
    # Determine index path
    if is_blog_subdir:
        index_path = '../index.html'
    else:
        index_path = 'index.html'
    
    # Determine language switch path
    basename = os.path.basename(filename)
    if is_en:
        lang_switch_path = basename.replace('-en.html', '.html')
        if is_blog_subdir:
            # For blog subdir, need to handle the path
            lang_switch_path = basename.replace('-en.html', '.html')
    else:
        lang_switch_path = basename.replace('.html', '-en.html')
    
    # Determine active states
    active_map = {
        'partners': 'text-blue-900 bg-blue-50',
        'platform': 'text-blue-900 bg-blue-50',
        'assets': 'text-blue-900 bg-blue-50',
        'blog': 'text-blue-900 bg-blue-50',
        'education': 'text-blue-900 bg-blue-50',
        'retirement': 'text-blue-900 bg-blue-50',
        'residency': 'text-blue-900 bg-blue-50',
        'index': 'text-blue-900 bg-blue-50',
        'other': 'text-gray-600 hover:text-blue-900 hover:bg-gray-100/50'
    }
    
    return NAV_TEMPLATE_TW.format(
        index_path=index_path,
        path_prefix=path_prefix,
        partners_active=active_map.get('partners') if page_type == 'partners' else active_map['other'],
        platform_active=active_map.get('platform') if page_type == 'platform' else active_map['other'],
        assets_active=active_map.get('assets') if page_type == 'assets' else active_map['other'],
        blog_active=active_map.get('blog') if page_type == 'blog' else active_map['other'],
        blog_active_mobile='text-blue-900 bg-blue-50' if page_type == 'blog' else 'text-gray-600 hover:bg-gray-50',
        lang_switch_path=lang_switch_path
    )

def generate_footer(filename):
    """Generate footer HTML for a specific file"""
    is_blog_subdir = is_in_blog_subdir(filename)
    
    if is_blog_subdir:
        path_prefix = '../'
    else:
        path_prefix = ''
    
    return FOOTER_TEMPLATE.format(path_prefix=path_prefix)

def process_file(filepath):
    """Process a single HTML file"""
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Generate new nav and footer
    new_nav = generate_nav(filepath)
    new_footer = generate_footer(filepath)
    
    # Replace navigation (look for various patterns)
    # Pattern 1: <!-- Navigation --> to <!-- Hero Section -->
    nav_pattern = r'<!-- Navigation -->.*?<!-- Hero Section -->'
    if re.search(nav_pattern, content, re.DOTALL):
        content = re.sub(nav_pattern, new_nav + '\n    <!-- Hero Section -->', content, flags=re.DOTALL)
    else:
        # Try alternative: find <nav> or <div class="fixed w-full z-50
        nav_alt_pattern = r'<nav[^>]*class="[^"]*fixed[^"]*z-50[^"]*"[^>]*>.*?</nav>'
        if re.search(nav_alt_pattern, content, re.DOTALL):
            # Find the position and replace
            pass  # Complex, skip for now
    
    # Replace footer
    footer_pattern = r'<!-- Footer -->.*?</footer>\s*</body>'
    if re.search(footer_pattern, content, re.DOTALL):
        content = re.sub(footer_pattern, new_footer + '\n</body>', content, flags=re.DOTALL)
    else:
        # Try alternative pattern
        footer_alt_pattern = r'<footer[^>]*class="[^"]*bg-\[#0f172a\][^"]*"[^>]*>.*?</footer>'
        if re.search(footer_alt_pattern, content, re.DOTALL):
            content = re.sub(footer_alt_pattern, new_footer, content, flags=re.DOTALL)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ Updated")

def main():
    """Main function"""
    # List of files to process (excluding backups and templates)
    files_to_process = []
    
    # Root directory files
    for filename in os.listdir(DIST_DIR):
        if filename.endswith('.html'):
            # Skip backups and templates
            if any(x in filename for x in ['-old', '-backup', 'temp', 'template', 'card.html', '404.html']):
                continue
            files_to_process.append(os.path.join(DIST_DIR, filename))
    
    # Blog subdirectory files
    blog_dir = os.path.join(DIST_DIR, 'blog')
    if os.path.exists(blog_dir):
        for filename in os.listdir(blog_dir):
            if filename.endswith('.html'):
                if any(x in filename for x in ['-old', '-backup', 'temp', 'template']):
                    continue
                files_to_process.append(os.path.join(blog_dir, filename))
    
    print(f"Found {len(files_to_process)} files to process")
    
    for filepath in files_to_process:
        try:
            process_file(filepath)
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\nDone!")

if __name__ == '__main__':
    main()