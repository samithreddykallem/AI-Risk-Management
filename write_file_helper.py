import os
import sys

def main():
    target_file = sys.argv[1]
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    content = sys.stdin.read()
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully wrote {target_file}")

if __name__ == "__main__":
    main()
