import re
import webbrowser
import os
import argparse
import random

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

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Open links from a markdown file categorized by headings.")
    parser.add_argument('--path', required=True, help="Path to the markdown file")
    parser.add_argument('--random', action='store_true', help="Open a random link instead of selecting manually")

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

    if args.random:
        # If --random flag is provided, choose a random link
        selected_url = random_link(categorized_links)
        if selected_url:
            open_in_browser(selected_url)
    else:
        # Otherwise, proceed with manual selection
        selected_url = display_menu(categorized_links)
        open_in_browser(selected_url)

if __name__ == "__main__":
    main()
