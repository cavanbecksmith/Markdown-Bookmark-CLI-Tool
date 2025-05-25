# Markdown Bookmark CLI Tool

usage
```
python link_viewer.py --path /path/test.md
python link_viewer.py --path /path/test.md --random
```

## Bash Setup

```
# Shared variables
export MUSIC_MD="/c/Users/winuser/folder_outside_protected_area/music.md"
export MUSIC_SCRIPT="/c/Users/winuser/Markdown-Bookmark-CLI-Tool/link_viewer.py"
export LINKS_MD="/c/Users/winuser/folder_outside_protected_area/links.md"

# Aliases
alias music="python $MD_SCRIPT --path=$MUSIC_MD"
alias musicr="python $MD_SCRIPT --path=$MUSIC_MD --random"
alias links="python $MD_SCRIPT --path=$LINKS_MD"
alias linksr="python $MD_SCRIPT --path=$LINKS_MD --random"

alias fixtitle="python $MD_SCRIPT --path=$LINKS_MD --fix-titles"

musicadd() {  # usage: musicadd <url> [category] [title]
    mdadd music "$@"
}

linkadd() {   # usage: linkadd <url> [category] [title]
    mdadd links "$@"
}

# Generalized add function
mdadd() {
    local type="$1"
    local url="$2"
    local category="$3"
    local title="$4"

    if [[ "$type" != "music" && "$type" != "links" ]]; then
        echo "Usage: mdadd <music|links> <url> [category] [title]"
        return 1
    fi

    if [[ -z "$url" ]]; then
        echo "Usage: mdadd <music|links> <url> [category] [title]"
        return 1
    fi

    local file_var="${type^^}_MD"
    local file_path="${!file_var}"

    if [[ -z "$category" ]]; then
        echo "Select a category:"
        mapfile -t headings < <(grep '^## ' "$file_path" | sed 's/^## //')

        if [[ ${#headings[@]} -eq 0 ]]; then
            echo "No categories found in $file_path."
            return 1
        fi

        for i in "${!headings[@]}"; do
            printf "%2d. %s\n" $((i + 1)) "${headings[$i]}"
        done

        read -rp "Enter number: " choice
        if [[ ! "$choice" =~ ^[0-9]+$ || "$choice" -lt 1 || "$choice" -gt "${#headings[@]}" ]]; then
            echo "Invalid selection."
            return 1
        fi

        category="${headings[$((choice - 1))]}"
    fi

    args=(--add "$url" "$category")
    [[ -n "$title" ]] && args+=("$title")

    python "$MD_SCRIPT" --path="$file_path" "${args[@]}"
}

# Generalized delete function
mddel() {
    local type="$1"
    local url="$2"
    local category="$3"

    if [[ "$type" != "music" && "$type" != "links" ]]; then
        echo "Usage: mddel <music|links> <url> <category>"
        return 1
    fi

    if [[ -z "$url" || -z "$category" ]]; then
        echo "Usage: mddel <music|links> <url> <category>"
        return 1
    fi

    local file_var="${type^^}_MD"
    local file_path="${!file_var}"

    python "$MD_SCRIPT" --path="$file_path" --delete "$url" "$category"
}
```

## Bash usage
```
# musicadd <url> <category> <title>
musicadd "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
musicadd "https://www.youtube.com/watch?v=dQw4w9WgXcQ" "Old school bangers" "A really good song"

# musicr - random song in list
# music - Select from all categories
```