#!/usr/bin/env python3
import re
import sys
import shutil

STRING_BLOCK_RE = re.compile(
    r'<string\s+name="([^"]+)"[^>]*>.*?</string>',
    re.DOTALL
)

def extract_blocks(xml_text):
    blocks = {}
    for m in STRING_BLOCK_RE.finditer(xml_text):
        key = m.group(1)
        blocks[key] = m.group(0)
    return blocks

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 merge_missing_strings.py <upstream.xml> <local.xml>")
        sys.exit(1)

    upstream_path, local_path = sys.argv[1], sys.argv[2]

    with open(upstream_path, "r", encoding="utf-8") as f:
        upstream_text = f.read()
    with open(local_path, "r", encoding="utf-8") as f:
        local_text = f.read()

    upstream_blocks = extract_blocks(upstream_text)
    local_blocks = extract_blocks(local_text)

    missing_keys = [k for k in upstream_blocks if k not in local_blocks]

    if not missing_keys:
        print("No missing keys - local file already has every upstream key.")
        return

    print(f"Found {len(missing_keys)} missing key(s). Inserting from upstream:")
    for k in missing_keys:
        print(f"  + {k}")

    backup_path = local_path + ".bak"
    shutil.copyfile(local_path, backup_path)
    print(f"\nBackup written to: {backup_path}")

    insertion = "\n" + "\n".join(
        "    " + upstream_blocks[k] for k in missing_keys
    ) + "\n"

    if "</resources>" not in local_text:
        print("Error: </resources> not found in local file - aborting, no changes made.")
        return

    new_text = local_text.replace("</resources>", insertion + "</resources>")

    with open(local_path, "w", encoding="utf-8") as f:
        f.write(new_text)

    print(f"\nDone. {len(missing_keys)} key(s) merged into {local_path}")
    print("Review the diff before committing:")
    print(f"  diff {backup_path} {local_path}")

if __name__ == "__main__":
    main()
