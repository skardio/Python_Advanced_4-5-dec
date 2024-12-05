from pathlib import Path

p = Path(".")

lst = list(p.glob("**/*.py"))

print(lst)