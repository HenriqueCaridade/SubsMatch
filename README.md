# Subs Match

This script matches the subtitle filenames to the video filenames of a given directory.

```
usage: subs_match [-h] [-f] [-p] [-s] [-q] [-v] [-y] [path-to-dir]

positional arguments:
  path-to-dir        path to directory where the files are, if not given uses CWD

options:
  -h, --help         show this help message and exit
  -f, --force        forces renaming/copying even if the files already have the correct name
  -p, --preserve     instead of renaming the subtitle files, they will be copied and the original files will be moved to a sub-directory
  -s, --skip-season  ignores season numbers if it doesn't find them (instead of defaulting to season 1)
  -q, --quiet        only show errors. Cannot be used without the --yes flag
  -v, --verbose      also show files found and parsing results
  -y, --yes          skip confirmation prompt
```

## How to run this script in any directory

- Step 1: Add script's directory to the PYTHONPATH environment variable
- Step 2: Run script with the following systax

```
python -m subs_match [args]
```

By running the script like this the cwd for the script will be set to the current directory.

