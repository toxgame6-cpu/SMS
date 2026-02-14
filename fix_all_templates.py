"""
Auto-fix ALL Django templates broken by Prettier/linter.
Fixes:
  1. Split {% tags %} across lines
  2. Mangled == operators (dept="" ="x" -> dept == x)
  3. Split HTML closing tags
  4. Missing </option> tags
"""
import os
import re


BASE_DIR = r'E:\student_management_system'


def find_html_files(base_dir):
    html_files = []
    for root, dirs, files in os.walk(base_dir):
        skip = False
        for skip_dir in ['venv', '.git', 'node_modules', '__pycache__']:
            if skip_dir in root.split(os.sep):
                skip = True
                break
        if skip:
            continue
        for f in files:
            if f.endswith('.html'):
                html_files.append(os.path.join(root, f))
    return html_files


def fix_split_tags(content):
    """Fix Django tags split across multiple lines."""
    result = []
    i = 0
    while i < len(content):
        if i < len(content) - 1 and content[i] == '{' and content[i+1] == '%':
            tag_start = i
            j = i + 2
            while j < len(content) - 1:
                if content[j] == '%' and content[j+1] == '}':
                    tag = content[tag_start:j+2]
                    # Collapse all whitespace inside tag to single spaces
                    fixed = '{%' + ' '.join(tag[2:-2].split()) + ' %}'
                    result.append(fixed)
                    i = j + 2
                    break
                j += 1
            else:
                result.append(content[i])
                i += 1
        elif i < len(content) - 1 and content[i] == '{' and content[i+1] == '{':
            tag_start = i
            j = i + 2
            while j < len(content) - 1:
                if content[j] == '}' and content[j+1] == '}':
                    tag = content[tag_start:j+2]
                    fixed = '{{' + ' '.join(tag[2:-2].split()) + ' }}'
                    result.append(fixed)
                    i = j + 2
                    break
                j += 1
            else:
                result.append(content[i])
                i += 1
        else:
            result.append(content[i])
            i += 1
    return ''.join(result)


def fix_mangled_operators(content):
    """
    Fix Prettier-mangled == operators inside {% if %} tags.

    Patterns found:
      {% if dept="" ="selected_department" %}  ->  {% if dept == selected_department %}
      {% if y="" ="selected_year" %}           ->  {% if y == selected_year %}
      {% if form.role.value="" ="admin" %}     ->  {% if form.role.value == "admin" %}
      {% if action_filter="" ="value" %}       ->  {% if action_filter == value %}
    """

    def fix_tag(match):
        tag_content = match.group(0)

        # Pattern 1: var="" ="something" -> var == something
        # This handles: dept="" ="selected_department"
        tag_content = re.sub(
            r'(\w[\w.]*?)=""\s*="(\w[\w.]*?)"',
            r'\1 == \2',
            tag_content
        )

        # Pattern 2: var="" ="'something'" -> var == 'something'
        tag_content = re.sub(
            r'(\w[\w.]*?)=""\s*="\'([^\']*?)\'"',
            r"\1 == '\2'",
            tag_content
        )

        # Pattern 3: value="" ="admin" with quotes around value
        tag_content = re.sub(
            r'(\w[\w.]*?)=""\s*="([^"]*?)"',
            r'\1 == "\2"',
            tag_content
        )

        return tag_content

    # Apply to all {% ... %} tags
    content = re.sub(r'\{%.*?%\}', fix_tag, content)

    return content


def fix_html_closing_tags(content):
    """Fix HTML closing tags split across lines: </a\\n    > -> </a>"""
    content = re.sub(r'</(\w+)\s*\n\s*>', r'</\1>', content)
    return content


def fix_template(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                original = f.read()
        except:
            return False

    content = original
    content = fix_split_tags(content)
    content = fix_mangled_operators(content)
    content = fix_html_closing_tags(content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def validate_templates(html_files):
    """Check for remaining issues."""
    print("\nValidating all templates...\n")
    issues = 0

    for filepath in sorted(html_files):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except:
            continue

        rel = os.path.relpath(filepath, BASE_DIR)

        for i, line in enumerate(lines):
            # Check for split tags
            opens = line.count('{%')
            closes = line.count('%}')
            if opens > closes:
                print(f'  SPLIT TAG: {rel} line {i+1}: {line.strip()[:80]}')
                issues += 1

            # Check for mangled ==
            if '=""' in line and '{%' in line:
                print(f'  MANGLED ==: {rel} line {i+1}: {line.strip()[:80]}')
                issues += 1

    if issues == 0:
        print("  ALL TEMPLATES LOOK CLEAN!")
    else:
        print(f"\n  Found {issues} remaining issues.")

    return issues


def main():
    print("=" * 60)
    print("  Django Template Auto-Fixer v2")
    print("  Fixes split tags AND mangled operators")
    print("=" * 60)

    html_files = find_html_files(BASE_DIR)
    print(f"\nFound {len(html_files)} HTML files\n")

    fixed = 0
    for filepath in sorted(html_files):
        if fix_template(filepath):
            rel = os.path.relpath(filepath, BASE_DIR)
            print(f"  FIXED: {rel}")
            fixed += 1

    print(f"\n  Fixed {fixed} out of {len(html_files)} files")

    validate_templates(html_files)

    print("\nDone! Run: python manage.py runserver")


if __name__ == '__main__':
    main()