#!/bin/bash

# Load environment
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$THIS_DIR/.md_env"

# Fallback to "python" if PY_COMMAND is not set
PY_COMMAND="${PY_COMMAND:-python3}"

# Map files from env into associative array
declare -A MD_FILES

alias linkstitlesfix="python $MD_SCRIPT --path=$MD_FILE_links --fix-titles"
alias musictitlesfix="python $MD_SCRIPT --path=$MD_FILE_music --fix-titles"

for var in ${!MD_FILE_*}; do
    key="${var#MD_FILE_}"
    MD_FILES["$key"]="${!var}"
done

# Create dynamic aliases and functions
for key in "${!MD_FILES[@]}"; do
    path="${MD_FILES[$key]}"

    alias "$key"="$PY_COMMAND \"$MD_SCRIPT\" --path=\"$path\""
    alias "${key}r"="$PY_COMMAND \"$MD_SCRIPT\" --path=\"$path\" --random"

    eval "${key}add() { mdadd \"$key\" \"\$@\"; }"
    eval "${key}del() { mddel \"$key\" \"\$@\"; }"
done

# Generalized add function
mdadd() {
    local key="$1"
    local url="$2"
    local category="$3"
    local title="$4"

    if [[ -z "${MD_FILES[$key]}" ]]; then
        echo "Invalid key: $key"
        return 1
    fi

    if [[ -z "$url" ]]; then
        echo "Usage: ${key}add <url> [category] [title]"
        return 1
    fi

    local file_path="${MD_FILES[$key]}"

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

    "$PY_COMMAND" "$MD_SCRIPT" --path="$file_path" "${args[@]}"
}

# Generalized delete function
mddel() {
    local key="$1"
    local url="$2"
    local category="$3"

    if [[ -z "${MD_FILES[$key]}" ]]; then
        echo "Invalid key: $key"
        return 1
    fi

    if [[ -z "$url" || -z "$category" ]]; then
        echo "Usage: ${key}del <url> <category>"
        return 1
    fi

    local file_path="${MD_FILES[$key]}"
    "$PY_COMMAND" "$MD_SCRIPT" --path="$file_path" --delete "$url" "$category"
}
