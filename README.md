# Subs Match

This script matches the subtitle filenames to the video filenames of a given directory.

```
usage: subs_match [-h] [-p] [-f] [path-to-dir]

positional arguments:
  path-to-dir     path to directory where the files are, if not given uses CWD

optional arguments:
  -h, --help      show this help message and exit
  -p, --preserve  instead of renaming the subtitle files, they will be copied and the original files will be moved to a sub-directory
  -f, --force     force rename/copy i.e. no confirmation prompt
```

## How to run this script in any directory

- Step 1: Add script's directory to the PYTHONPATH environment variable
- Step 2: Run script with the following systax

```
python -m subs_match [args]
```

By running the script like this the cwd for the script will be set to the current directory.

