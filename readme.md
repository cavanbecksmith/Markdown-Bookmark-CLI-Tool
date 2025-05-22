# Markdown Bookmark CLI Tool

usage
```
python link_viewer.py --path /path/test.md
python link_viewer.py --path /path/test.md --random
```

## Bash Setup

```
# Shared variables
export MUSIC_MD="/c/Users/winuser/folder_outside_protected_area/Bookmark.md"
export MUSIC_SCRIPT="/c/Users/winuser/Markdown-Bookmark-CLI-Tool/link_viewer.py"

# Aliases
alias music="python $MUSIC_SCRIPT --path=$MUSIC_MD"
alias musicr="python $MUSIC_SCRIPT --path=$MUSIC_MD --random"

# Add function
musicadd() {
    local url="$1"
    local category="$2"
    local title="$3"

    if [[ -z "$url" ]]; then
        echo "Usage: musicadd <url> [category] [title]"
        return 1
    fi

    args=(--add "$url")
    [[ -n "$category" ]] && args+=("$category")
    [[ -n "$title" ]] && args+=("$title")

    python "$MUSIC_SCRIPT" --path="$MUSIC_MD" "${args[@]}"
}

# Delete function
musicdel() {
    local url="$1"
    local category="$2"

    if [[ -z "$url" || -z "$category" ]]; then
        echo "Usage: musicdel <url> <category>"
        return 1
    fi

    python "$MUSIC_SCRIPT" --path="$MUSIC_MD" --delete "$url" "$category"
}

```

## Bash usage
```
musicadd "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
musicadd 
```