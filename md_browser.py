import os
import re
import sys
import webbrowser
from collections import defaultdict

def parse_markdown(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    data = defaultdict(lambda: {"links": [], "entries": {}})
    current_category = None
    current_subheading = None
    buffer = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("## "):
            if current_subheading and buffer:
                data[current_category]["entries"][current_subheading] = "\n".join(buffer).strip()
                buffer = []
            current_category = stripped[3:].strip()
            current_subheading = None
        elif stripped.startswith("### "):
            if current_subheading and buffer:
                data[current_category]["entries"][current_subheading] = "\n".join(buffer).strip()
                buffer = []
            current_subheading = stripped[4:].strip()
        elif re.match(r"- \[.*\]\(.*\)", stripped):
            match = re.match(r"- \[(.*?)\]\((.*?)\)", stripped)
            if match:
                title, url = match.groups()
                data[current_category]["links"].append((title, url))
        elif current_subheading:
            buffer.append(line.rstrip())

    if current_category and current_subheading and buffer:
        data[current_category]["entries"][current_subheading] = "\n".join(buffer).strip()

    return data

def write_markdown(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        for category, content in data.items():
            f.write(f"## {category}\n\n")
            for title, url in content["links"]:
                f.write(f"- [{title}]({url})\n")
            if content["links"]:
                f.write("\n")
            for subheading, text in content["entries"].items():
                f.write(f"### {subheading}\n{text}\n\n")

def choose_from_list(items, title="Choose an option:"):
    print(f"\n{title}")
    for i, item in enumerate(items, 1):
        print(f"{i}. {item}")
    while True:
        try:
            choice = int(input("> "))
            if 1 <= choice <= len(items):
                return items[choice - 1]
        except ValueError:
            pass
        print("Invalid input, try again.")

def add_entry(data, filepath):
    category = choose_from_list(list(data.keys()), "Select category to add content to:")
    heading = input("Enter subheading title (H3): ").strip()
    if not heading:
        print("❌ Subheading cannot be empty.")
        return
    print("Enter the content (Markdown supported). Type '::done' on a new line to finish:")
    lines = []
    while True:
        line = input()
        if line.strip() == "::done":
            break
        lines.append(line)
    content = "\n".join(lines).strip()
    if content:
        data[category]["entries"][heading] = content
        write_markdown(filepath, data)
        print(f"✅ Added content under '{heading}' in '{category}'.")
    else:
        print("❌ Content was empty. Nothing added.")

def delete_entry(data, filepath):
    category = choose_from_list(list(data.keys()), "Select category:")
    entries = list(data[category]["entries"].keys())
    if not entries:
        print("No subheadings to delete in this category.")
        return
    heading = choose_from_list(entries, "Select subheading to delete:")
    del data[category]["entries"][heading]
    write_markdown(filepath, data)
    print(f"🗑️ Deleted subheading '{heading}' from '{category}'.")

def browse(data):
    categories = list(data.keys())
    selected_category = choose_from_list(categories, "Select a category:")
    entries = list(data[selected_category]["entries"].keys())
    links = data[selected_category]["links"]
    combined = entries + [f"{title} (link)" for title, _ in links]

    if not combined:
        print("No entries or links in this category.")
        return

    selected_item = choose_from_list(combined, f"{selected_category}: Choose an entry or link:")

    if selected_item.endswith("(link)"):
        index = combined.index(selected_item) - len(entries)
        _, url = links[index]
        print(f"Opening {url}...")
        webbrowser.open(url)
    else:
        print(f"\n--- {selected_item} ---")
        print(data[selected_category]["entries"][selected_item])

def main():
    if len(sys.argv) < 2:
        print("Usage: python md_browser.py <markdown_file> [browse|add|delete]")
        return

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"Markdown file '{filepath}' not found.")
        return

    action = sys.argv[2] if len(sys.argv) > 2 else "browse"
    data = parse_markdown(filepath)

    if action == "browse":
        browse(data)
    elif action == "add":
        add_entry(data, filepath)
    elif action == "delete":
        delete_entry(data, filepath)
    else:
        print(f"Unknown action: {action}")
        print("Valid actions: browse, add, delete")

if __name__ == "__main__":
    main()
