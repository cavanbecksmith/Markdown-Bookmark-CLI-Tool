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
    shift
    local url=""
    local category=""
    local title=""
    local auto_flag=""
    local prompt_flag=""

    if [[ -z "${MD_FILES[$key]}" ]]; then
        echo "Invalid key: $key"
        return 1
    fi

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -a|--auto)
                auto_flag="--auto"
                shift
                ;;
            -p|--prompt)
                prompt_flag="--prompt"
                shift
                ;;
            *)
                if [[ -z "$url" ]]; then
                    url="$1"
                elif [[ -z "$category" ]]; then
                    category="$1"
                elif [[ -z "$title" ]]; then
                    title="$1"
                fi
                shift
                ;;
        esac
    done

    if [[ -z "$url" ]]; then
        echo "Usage: ${key}add <url> [category] [title] [-a|--auto] [-p|--prompt]"
        echo "  -a, --auto    Automatically fetch title from URL"
        echo "  -p, --prompt  Prompt user to enter title manually"
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
    [[ -n "$auto_flag" ]] && args+=("$auto_flag")
    [[ -n "$prompt_flag" ]] && args+=("$prompt_flag")

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
