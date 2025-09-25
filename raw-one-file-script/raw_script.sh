#!/bin/bash

# Usage: ./script.sh [repo_directory]
REPO_DIR="${1:-.}"

# check if repo directory exists
if [ ! -d "$REPO_DIR" ]; then
    echo "[ERROR] Directory '$REPO_DIR' does not exist."
    exit 1
fi

# get absolute path to script location
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# create central repo_dump folder next to script
DUMP_DIR="$SCRIPT_DIR/repo_dump"
mkdir -p "$DUMP_DIR"

# timestamped output file
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT="$DUMP_DIR/repo_dump_$TIMESTAMP.txt"

echo "[INFO] Creating repo dump: $OUTPUT"

# gather file list (respecting .gitignore, skip repo_dump)
FILES=$(cd "$REPO_DIR" && git ls-files --cached --others --exclude-standard | grep -v '^repo_dump/')
TOTAL=$(echo "$FILES" | wc -l)

echo "[INFO] Processing $TOTAL files..."
echo

# prepare progress checkpoints (10%, 20%, ...)
CHECKPOINTS=$(seq 10 10 100)
NEXT_CHECKPOINT=10

COUNT=0

(
    for file in $FILES; do
        COUNT=$((COUNT + 1))
        echo "##### $file #####"
        cat "$REPO_DIR/$file"
        echo -e "\n"

        # log progress only at checkpoints
        PERCENT=$((COUNT * 100 / TOTAL))
        if [ $PERCENT -ge $NEXT_CHECKPOINT ]; then
            echo "[INFO] $NEXT_CHECKPOINT% completed ($COUNT/$TOTAL files)" >&2
            NEXT_CHECKPOINT=$((NEXT_CHECKPOINT + 10))
        fi
    done
) > "$OUTPUT"

# stats
LINES=$(wc -l < "$OUTPUT")
SIZE=$(du -h "$OUTPUT" | cut -f1)
CHARS=$(wc -m < "$OUTPUT")
TOKENS=$((CHARS / 4))

echo
echo "[DONE] Repo dump created: $OUTPUT"
echo "[INFO] Total files processed: $TOTAL"
echo "[INFO] Total lines in dump: $LINES"
echo "[INFO] Total size of dump: $SIZE"
echo "[INFO] Approx token count (chars/4): $TOKENS"
echo "[INFO] Script finished at: $(date +"%Y-%m-%d %H:%M:%S")"