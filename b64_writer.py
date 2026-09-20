import sys
import os
import base64

if len(sys.argv) < 3:
    print("Usage: python b64_writer.py <target_path> <b64_content>")
    sys.exit(1)

target_path = sys.argv[1]
b64_str = sys.argv[2]
content = base64.b64decode(b64_str).decode("utf-8")

os.makedirs(os.path.dirname(target_path), exist_ok=True)
with open(target_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully wrote {target_path}")
