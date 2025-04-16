# Subs Match

This script matches the subtitle filenames to the video filenames of a given directory.

```
usage: subs_match [-h] [-f] [-n] [-p] [-s] [-q] [-v] [-y] [path-to-dir]

positional arguments:
  path-to-dir        path to directory where the files are, if not given uses CWD

optional arguments:
  -h, --help         show this help message and exit
  -f, --force        forces renaming/copying even if the files already have the correct name
  -n, --no-color     removes ANSI codes used for the colors.
  -p, --preserve     instead of renaming the subtitle files, they will be copied and the original files will be moved to a sub-directory
  -s, --skip-season  ignores season numbers if it doesn't find them (instead of defaulting to season 1)
  -q, --quiet        only show errors. Cannot be used without the --yes flag
  -v, --verbose      also show files found and parsing results
  -y, --yes          skip confirmation prompt
```

## How to run this script in any directory

- Step 1: Add script's directory to the PYTHONPATH environment variable (create variable if it doesn't exist)
- Step 2: Run script with `python -m subs_match [args]`

By running the script like this the cwd for the script will be set to the current directory.

## How to run any script without adding each to the PYTHONPATH

- Step 1: Create a new directory in your scripts folder, for example, `.pypath`
- Step 2: Add this new directory to the PYTHONPATH enviroment variable (create variable if it doesn't exist)
- Step 3: Add to this directory the following script (one for each script you want to be able to run from any directory)
- Step 4: Run the script with the same syntax as before `python -m <your-script-name> [args]`

This script simply "redirects" the call to the correct location.

**Important Note:** the name of this "redirecting" file is the one you have to use when calling with `python -m <your-script-name> [args]`

**Linux Note:** if on linux change `python` to `python3`
```py
from pathlib import Path
import os, sys
p = Path(__file__).parent.parent / 'path' / 'to' / 'your' / 'script.py'
args = ' '.join(map(lambda arg: arg if ' ' not in arg else f'"{arg}"', sys.argv[1:]))
try:
    os.system(f'python "{p}" {args}')
except KeyboardInterrupt:
    pass
```
