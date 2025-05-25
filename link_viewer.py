import re
import webbrowser
import os
import argparse
import random
import requests

def parse_markdown(file_path):
    """
    Parse the markdown file, extract headings and links categorized by headings.
    Compatible with UTF-8 files across Windows and Linux.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()

    # Regex pattern to capture headings and links
    headings = re.findall(r'^(##)\s*(.*)', content, re.MULTILINE)
    links = re.findall(r'\[([^\]]+)\]\((http[^\)]+)\)', content)

    categorized_links = {}
    current_heading = None

    # Categorize links under respective headings
    for line in content.splitlines():
        heading_match = re.match(r'^(##)\s*(.*)', line)
        if heading_match:
            current_heading = heading_match.group(2).strip()
            categorized_links[current_heading] = []
        elif current_heading and re.search(r'\[([^\]]+)\]\((http[^\)]+)\)', line):
            link_match = re.search(r'\[([^\]]+)\]\((http[^\)]+)\)', line)
            if link_match:
                link_text = link_match.group(1)
                link_url = link_match.group(2)
                categorized_links[current_heading].append((link_text, link_url))

    return categorized_links


def display_menu(categorized_links):
    """
    Display a menu of headings and their links for the user to choose from.
    """
    print("Select a category:")
    headings = list(categorized_links.keys())
    for i, heading in enumerate(headings, 1):
        print(f"{i}. {heading}")

    heading_choice = int(input("\nEnter the number corresponding to the category: ")) - 1
    selected_heading = headings[heading_choice]

    print(f"\nLinks under '{selected_heading}':")
    for i, (link_text, link_url) in enumerate(categorized_links[selected_heading], 1):
        print(f"{i}. {link_text}")

    link_choice = int(input("\nEnter the number of the link you want to open: ")) - 1
    selected_link = categorized_links[selected_heading][link_choice][1]
    
    return selected_link

def random_link(categorized_links):
    """
    Select a random link from all available links across all categories.
    """
    all_links = []
    for heading in categorized_links.values():
        all_links.extend(heading)  # Flatten the list of links

    if not all_links:
        print("No links available.")
        return None

    random_choice = random.choice(all_links)  # Choose a random link
    return random_choice[1]  # Return the URL

def open_in_browser(url):
    """
    Open the selected URL in the default web browser.
    """
    print(f"Opening: {url}")
    webbrowser.open(url)


def add_link(markdown_file, title, url, category, categorized_links):
    """
    Add a link to the specified category in the markdown file.
    If title is None, fetch it from the URL.
    If category is None, default to '⭐'.
    """
    if category is None:
        category = '⭐'

    if title is None:
        try:
            import requests
            from bs4 import BeautifulSoup
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else url
        except Exception:
            title = url

    # Build the markdown link
    markdown_link = f"[#{title}]({url})\n"

    with open(markdown_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Locate the category heading
    cat_heading = f"## {category}"
    new_lines = []
    inserted = False
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        if line.strip() == cat_heading:
            i += 1
            # Skip past existing links under the heading
            while i < len(lines) and not lines[i].startswith('## '):
                new_lines.append(lines[i])
                i += 1
            # Append the new link just before the next heading or EOF
            new_lines.insert(len(new_lines), markdown_link)
            inserted = True
            continue
        i += 1

    # If the category wasn't found, create it at the end
    if not inserted:
        new_lines.append(f"\n{cat_heading}\n")
        new_lines.append(markdown_link)

    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"Added to '{category}': {markdown_link.strip()}")


def fetch_title(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
    except Exception as e:
        print(f"⚠️  Could not fetch title from {url}: {e}")
    return None

def fix_bare_links(markdown_file, stdout=False):
    url_pattern = re.compile(r'^\s*(https?://\S+)\s*$')
    link_pattern = re.compile(r'^\s*\[.*\]\(https?://\S+\)\s*$')

    updated_lines = []
    updated = False

    with open(markdown_file, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()

            # Leave category headings and markdown links unchanged
            if stripped.startswith("##") or link_pattern.match(stripped):
                updated_lines.append(line)
                continue

            # Bare URL line?
            url_match = url_pattern.match(stripped)
            if url_match:
                url = url_match.group(1)
                print(f"🔍 Fetching title for: {url}")
                title = fetch_title(url)
                if title:
                    formatted = f"[{title}]({url})\n"
                    updated_lines.append(formatted)
                    updated = True
                    print(f"✅ Converted to: {formatted.strip()}")
                else:
                    print(f"⚠️  Could not fetch title for: {url}")
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

    if stdout:
        print("\n📄 Final Output:\n" + "-" * 40)
        for line in updated_lines:
            print(line, end="")
        print("\n" + "-" * 40)
        print("✅ Preview complete. No file written.")
    else:
        if updated:
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)
            print("✅ File updated with new titles.")
        else:
            print("ℹ️  No bare links found to update.")

def delete_link(file_path, url, category):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_category = False
    modified_lines = []
    removed = False

    for line in lines:
        if line.strip().startswith("## "):
            in_category = (line.strip() == f"## {category}")
            modified_lines.append(line)
        elif in_category and f"]({url})" in line:
            removed = True
            print(f"🗑️  Removed: {line.strip()}")
            continue  # Skip this line
        else:
            modified_lines.append(line)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(modified_lines)

    if not removed:
        print("⚠️  Link not found.")


def main():
    parser = argparse.ArgumentParser(description="Manage categorized links in a markdown file.")
    parser.add_argument('--path', required=True, help="Path to the markdown file")

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--random', action='store_true', help="Open a random link")
    group.add_argument('--add', nargs='+', metavar=('URL', 'CATEGORY', 'TITLE'), help="Add a link: URL CATEGORY [TITLE]")
    group.add_argument('--delete', nargs=2, metavar=('URL', 'CATEGORY'), help="Delete a link")
    group.add_argument('--fix-titles', action='store_true', help="Fetch and update missing link titles")

    args = parser.parse_args()
    markdown_file = args.path

    if not os.path.exists(markdown_file):
        print("File does not exist.")
        return

    # Parse markdown to dictionary structure
    categorized_links = parse_markdown(markdown_file)

    if args.add:
        url = args.add[0]
        category = "⭐"
        title = None

        if len(args.add) >= 2 and args.add[1].strip():
            category = args.add[1].strip()

        if len(args.add) == 3 and args.add[2].strip():
            title = args.add[2].strip()

        if not title:
            title = fetch_title(url)

        add_link(markdown_file, title, url, category, categorized_links)

    elif args.delete:
        url, category = args.delete
        delete_link(markdown_file, url, category)

    elif args.random:
        selected_url = random_link(categorized_links)
        if selected_url:
            open_in_browser(selected_url)
    elif args.fix_titles:
        fix_bare_links(markdown_file)
    else:
        selected_url = display_menu(categorized_links)
        open_in_browser(selected_url)

if __name__ == "__main__":
    main()