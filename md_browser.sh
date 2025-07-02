#!/bin/bash

# Load environment
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$THIS_DIR/.md_env"

# Fallback to "python3" if not specified
PY_COMMAND="${PY_COMMAND:-python3}"

# Map files from env into associative array
declare -A NOTE_FILES

# Build aliases for each markdown file
for var in ${!NOTE_FILE_*}; do
    key="${var#NOTE_FILE_}"
    NOTE_FILES["$key"]="${!var}"
done

# Create per-key commands
for key in "${!NOTE_FILES[@]}"; do
    path="${NOTE_FILES[$key]}"

    alias "$key"="$PY_COMMAND \"$NOTES_MD_SCRIPT\" \"$path\""             # browse
    alias "${key}r"="$PY_COMMAND \"$NOTES_MD_SCRIPT\" \"$path\" --random" # random

    eval "${key}add() { noteadd \"$key\"; }"
    eval "${key}del() { notedel \"$key\"; }"
done

# Generalized add function (for content, not links)
noteadd() {
    local key="$1"
    if [[ -z "${NOTE_FILES[$key]}" ]]; then
        echo "Invalid key: $key"
        return 1
    fi
    local file_path="${NOTE_FILES[$key]}"
    "$PY_COMMAND" "$NOTES_MD_SCRIPT" "$file_path" "add"
}

# Generalized delete function (interactive)
notedel() {
    local key="$1"
    if [[ -z "${NOTE_FILES[$key]}" ]]; then
        echo "Invalid key: $key"
        return 1
    fi
    local file_path="${NOTE_FILES[$key]}"
    "$PY_COMMAND" "$NOTES_MD_SCRIPT" --path="$file_path" --delete
}