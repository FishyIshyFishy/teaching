"""Decode Tiny CPU Challenge verify codes.

Each code looks like  PAYLOAD-CHECK  (e.g. "01A3-4F2B").
  PAYLOAD  base-36, packs (task index, size, pass) as ((task*100 + size)*2 + pass)
  CHECK    first 4 hex chars of FNV-1a( name | payload | secret )

The checksum is bound to the student's name, so a code copied from someone
else (or an edited screenshot) fails validation once you pass the right name.

For now this just reads/decodes. Later: read a spreadsheet of (name, code)
rows and write a points column.
"""

verify_secret = "sand2cpu"

# Must match the task order and parSize values in tiny_cpu_challenge.html.
task_names = ["Copy", "Add two", "Sum four", "Difference",
              "Triple it", "Multiply", "Divide", "Square (bonus)"]
task_par_size = [2, 3, 5, 3, 4, 10, 9, 12]


def fnv(text):
    h = 2166136261
    for ch in text:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return format(h, "08X")


def decode(code, name):
    """Return a dict describing one verify code, checked against `name`."""
    body, _, check = code.strip().upper().partition("-")
    payload = int(body, 36)
    expected = fnv(f"{name}|{payload}|{verify_secret}")[:4]

    passed = bool(payload & 1)
    ts = payload >> 1
    size = ts % 100
    task = ts // 100

    return {
        "task": task,
        "task_name": task_names[task] if task < len(task_names) else "?",
        "size": size,
        "par_size": task_par_size[task] if task < len(task_par_size) else None,
        "passed": passed,
        "valid": check == expected,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("usage: tiny_cpu_grade.py <verify-code> <student-name>")
        raise SystemExit(1)
    info = decode(sys.argv[1], sys.argv[2])
    print(info)
