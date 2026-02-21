import os
import re

CSS_DIR = "static/css"
JS_DIR = "static/js"

os.makedirs(CSS_DIR, exist_ok=True)
os.makedirs(JS_DIR, exist_ok=True)

files_to_process = {
    "candidatos/templates/candidatos/base.html": "base",
    "candidatos/templates/candidatos/candidato_detail.html": "candidato_detail",
    "candidatos/templates/candidatos/home.html": "home",
    "candidatos/templates/candidatos/quiz.html": "quiz",
    "candidatos/templates/candidatos/comparar.html": "comparar",
}

for filepath, name in files_to_process.items():
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    original_content = content
    
    styles_extracted = False
    scripts_extracted = False
    
    # Extract CSS
    style_pattern = re.compile(r'<style>(.*?)</style>', re.DOTALL)
    styles = style_pattern.findall(content)
    if styles:
        combined_css = "\n".join(styles).strip()
        if combined_css:
            css_path = os.path.join(CSS_DIR, f"{name}.css")
            with open(css_path, "w", encoding="utf-8") as f:
                f.write(combined_css)
            # Replace inline style with link tag
            def style_repl(match):
                if not hasattr(style_repl, "done"):
                    style_repl.done = True
                    return f'<link rel="stylesheet" href="{{% static \'css/{name}.css\' %}}">'
                return ""
            content = style_pattern.sub(style_repl, content)
            styles_extracted = True

    # Extract JS
    script_pattern = re.compile(r'<script>(.*?)</script>', re.DOTALL)
    scripts = script_pattern.findall(content)
    if scripts:
        combined_js = "\n".join([s for s in scripts if s.strip() and not 'src=' in s and not 'http' in s]).strip()
        # Some empty scripts or CDNs need ignoring. Wait, the pattern above catches internal content. Let's just catch anything inside.
        # Actually in base.html there is a bootstrap script tag:
        # <script src="https://..."></script> which has no content.
        if combined_js:
            js_path = os.path.join(JS_DIR, f"{name}.js")
            with open(js_path, "w", encoding="utf-8") as f:
                f.write(combined_js)
            def script_repl(match):
                inner = match.group(1).strip()
                if not inner: 
                    return match.group(0) # Keep empty script tags (e.g if they had src attribute, wait, <script...> is not matched by <script> tag pattern!!
                if not hasattr(script_repl, "done"):
                    script_repl.done = True
                    return f'<script src="{{% static \'js/{name}.js\' %}}"></script>'
                return ""
            content = script_pattern.sub(script_repl, content)
            scripts_extracted = True

    # Check if load static is needed
    if (styles_extracted or scripts_extracted) and "{% load static %}" not in content:
        if "{% extends" in content:
            content = re.sub(r'({% extends .*? %})', r'\1\n{% load static %}', content, count=1)
        else:
            content = "{% load static %}\n" + content

    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    
    print(f"Processed {filepath}")
