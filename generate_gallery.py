#!/usr/bin/env python3
"""
自动生成和更新网页画廊页面的脚本
用于扫描图片和代码文件，并生成对应的HTML页面
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple


class GalleryGenerator:
    def __init__(self, img_base_path: str, pages_base_path: str):
        """
        初始化生成器
        
        Args:
            img_base_path: 图片和代码文件所在的基础路径，如 '网页/img'
            pages_base_path: HTML页面输出路径，如 '网页/pages'
        """
        self.img_base_path = Path(img_base_path)
        self.pages_base_path = Path(pages_base_path)
        
    def extract_description_from_md(self, md_file_path: Path) -> str:
        """
        从Markdown文件中提取描述（注释行）
        
        Args:
            md_file_path: Markdown文件路径
            
        Returns:
            描述文本
        """
        try:
            with open(md_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 查找代码块中的注释行（以 # 开头）
            # 支持 R、r、python、Python 等多种语言标记
            comment_match = re.search(r'```(?:r|R|python|Python)\s*\n#\s*(.+?)\n', content)
            if comment_match:
                return comment_match.group(1).strip()
            
            # 如果没有找到注释，返回默认描述
            return "代码示例"
        except Exception as e:
            print(f"警告: 无法读取文件 {md_file_path}: {e}")
            return "代码示例"
    
    def extract_code_from_md(self, md_file_path: Path) -> str:
        """
        从Markdown文件中提取代码块
        
        Args:
            md_file_path: Markdown文件路径
            
        Returns:
            代码内容
        """
        try:
            with open(md_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 提取代码块内容
            # 支持 R、r、python、Python 等多种语言标记
            code_match = re.search(r'```(?:r|R|python|Python)\s*\n(.*?)\n```', content, re.DOTALL)
            if code_match:
                return code_match.group(1).strip()
            
            return ""
        except Exception as e:
            print(f"警告: 无法读取文件 {md_file_path}: {e}")
            return ""
    
    def scan_directory(self, dir_name: str) -> List[Dict[str, str]]:
        """
        扫描指定目录下的图片和Markdown文件
        
        Args:
            dir_name: 目录名称，如 'R code' 或 'Python code'
            
        Returns:
            包含图片和代码信息的字典列表
        """
        target_dir = self.img_base_path / dir_name
        if not target_dir.exists():
            print(f"警告: 目录不存在 {target_dir}")
            return []
        
        items = []
        # 查找所有.md文件
        for md_file in sorted(target_dir.glob('*.md')):
            # 查找对应的图片文件
            base_name = md_file.stem
            png_file = target_dir / f"{base_name}.png"
            
            if png_file.exists():
                description = self.extract_description_from_md(md_file)
                code = self.extract_code_from_md(md_file)
                
                items.append({
                    'title': base_name,
                    'description': description,
                    'image_path': f"../img/{dir_name}/{png_file.name}",
                    'code': code,
                })
        
        return items
    
    def detect_language(self, dir_name: str) -> Tuple[str, str]:
        """
        根据目录名检测编程语言
        
        Args:
            dir_name: 目录名称
            
        Returns:
            (语言名称, Prism语言代码)
        """
        dir_lower = dir_name.lower()
        if 'r code' in dir_lower or 'r-code' in dir_lower:
            return ('R', 'r')
        elif 'python' in dir_lower:
            return ('Python', 'python')
        elif 'javascript' in dir_lower or 'js' in dir_lower:
            return ('JavaScript', 'javascript')
        else:
            return ('Code', 'plaintext')
    
    def generate_html_content(self, dir_name: str, items: List[Dict[str, str]]) -> str:
        """
        生成HTML内容
        
        Args:
            dir_name: 目录名称
            items: 项目列表
            
        Returns:
            完整的HTML内容
        """
        lang_name, lang_code = self.detect_language(dir_name)
        page_title = f"{lang_name} Code Gallery"
        
        # 生成画廊项目HTML
        gallery_items_html = ""
        for i, item in enumerate(items, 1):
            gallery_items_html += f"""
            <!-- Item {i}: {item['title']} -->
            <div class="gallery-item">
                <div class="gallery-image-wrapper">
                    <img src="{item['image_path']}" alt="{item['title']}" class="gallery-image">
                    <div class="gallery-overlay">
                        <button class="view-code-btn" onclick="openModal('modal-{i}')">查看代码</button>
                    </div>
                </div>
                <div class="gallery-info">
                    <h3 class="gallery-item-title">{item['title']}</h3>
                    <p class="gallery-item-description">{item['description']}</p>
                </div>
            </div>
"""
        
        # 生成模态框HTML
        modals_html = ""
        for i, item in enumerate(items, 1):
            modals_html += f"""
    <!-- Modal {i}: {item['title']} -->
    <div id="modal-{i}" class="modal">
        <div class="modal-content">
            <span class="modal-close" onclick="closeModal('modal-{i}')">&times;</span>
            <h2>{item['title']} - {lang_name} Code</h2>
            <pre><code class="language-{lang_code}">{item['code']}</code></pre>
            <div class="modal-image">
                <img src="{item['image_path']}" alt="{item['title']}">
            </div>
        </div>
    </div>
"""
        
        # 生成Prism语言组件URL
        prism_lang_component = f"https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-{lang_code}.min.js"
        
        # 完整HTML模板
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <link rel="stylesheet" href="../css/styles.css">
    <link rel="stylesheet" href="../css/gallery.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
</head>
<body class="dark">
    <!-- Background Canvas -->
    <canvas id="background-canvas"></canvas>

    <!-- Top navigation -->
    <nav class="top-nav fade-in">
        <a href="../index.html">Home</a>
        <a href="introduction.html">Introduction</a>
        <a href="r-code.html">R code</a>
        <a href="python-code.html">Python code</a>
        <a href="other-code.html">Other code</a>
    </nav>

    <!-- Main content -->
    <main class="gallery-content fade-in">
        <h1 class="gallery-title">{page_title}</h1>
        
        <div class="gallery-grid">
{gallery_items_html}
        </div>
    </main>

    <!-- Footer -->
    <footer class="footer fade-in">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h4>代码空间</h4>
                    <p>提供简洁美观的代码。</p>
                    <div class="footer-social">
                        <a href="https://www.webofscience.com/wos/author/record/491521" class="social-link">Obsidian</a>
                        <a href="https://www.webofscience.com/wos/author/record/491521" class="social-link">Web of Science</a>
                        <a href="https://scholar.google.com/citations?user=FLRq3GEAAAAJ&hl=zh-TW&oi=sra" class="social-link">Google Scholar</a>
                        <a href="https://www.researchgate.net/profile/Guanglin-He-heguanglin-2/research" class="social-link">Research Gate</a>
                    </div>
                </div>
                <div class="footer-section">
                    <h4>联系我们</h4>
                    <div class="contact-info">
                        <p>📧 gianthuihui@gmail.com</p>
                    </div>
                </div>
            </div>
            <div class="footer-bottom">
                <p><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">蜀ICP备2025140770号-3</a> &copy; </p>
            </div>
        </div>
    </footer>

    <!-- Modals for code display -->
{modals_html}

    <script src="../js/page-load.js"></script>
    <script src="../js/background.js"></script>
    <script src="../js/modal.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    <script src="{prism_lang_component}"></script>
</body>
</html>
"""
        return html_content
    
    def generate_page(self, dir_name: str, output_filename: str = None):
        """
        生成单个页面
        
        Args:
            dir_name: img目录下的子目录名，如 'R code'
            output_filename: 输出文件名，如 'r-code.html'，如果为None则自动生成
        """
        # 扫描目录
        items = self.scan_directory(dir_name)
        
        if not items:
            print(f"警告: 在 {dir_name} 中没有找到任何项目")
            return
        
        # 生成HTML
        html_content = self.generate_html_content(dir_name, items)
        
        # 确定输出文件名
        if output_filename is None:
            output_filename = dir_name.lower().replace(' ', '-') + '.html'
        
        # 写入文件
        output_path = self.pages_base_path / output_filename
        self.pages_base_path.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ 成功生成: {output_path}")
        print(f"  - 包含 {len(items)} 个项目")


def main():
    """主函数"""
    # 配置路径（根据实际情况修改）
    import sys
    
    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    img_base = script_dir / "img"
    pages_base = script_dir / "pages"
    
    # 创建生成器
    generator = GalleryGenerator(img_base, pages_base)
    
    # 生成页面
    print("开始生成画廊页面...\n")
    
    # R code页面
    generator.generate_page("R code", "r-code.html")
    
    # Python code页面（如果存在）
    if (Path(img_base) / "Python code").exists():
        generator.generate_page("Python code", "python-code.html")
    
    print("\n所有页面生成完成！")


if __name__ == "__main__":
    main()
