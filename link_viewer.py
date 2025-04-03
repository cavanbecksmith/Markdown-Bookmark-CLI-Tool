import re
import webbrowser
import os
import argparse

def parse_markdown(file_path):
    """
    Parse the markdown file, extract headings and links categorized by headings.
    """
    with open(file_path, 'r') as f:
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

def open_in_browser(url):
    """
    Open the selected URL in the default web browser.
    """
    print(f"Opening: {url}")
    webbrowser.open(url)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Open links from a markdown file categorized by headings.")
    parser.add_argument('--path', required=True, help="Path to the markdown file")
    
    # Parse arguments
    args = parser.parse_args()
    markdown_file = args.path

    if not os.path.exists(markdown_file):
        print("File does not exist.")
        return

    categorized_links = parse_markdown(markdown_file)
    
    if not categorized_links:
        print("No headings or links found in the markdown file.")
        return

    selected_url = display_menu(categorized_links)
    open_in_browser(selected_url)

if __name__ == "__main__":
    main()

