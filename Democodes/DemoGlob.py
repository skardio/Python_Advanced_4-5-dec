from pathlib import Path

p = Path(".")

lstFiles = list(p.glob("**/*.py"))

print(lstFiles)

print(lstFiles[0].is_dir())
print(lstFiles[0].is_file())
