# Subs Match

This script matches the subtitle filenames to the video filenames of a given directory.

## Index
1. [Usage](#usage)
1. [Full Usage](#full-usage)
1. [How to run this script in any directory](#how-to-run-this-script-in-any-directory)
1. [How to run any script without adding each to the PYTHONPATH](#how-to-run-any-script-without-adding-each-to-the-pythonpath)

## Usage

Step 0: If you didn't add script to PYTHONPATH as described below, copy script `subs_match.py` into the diretory.

Directory:
```
S01E01 - Breaking Bad - Pilot.mkv
S01E02 - Breaking Bad - Cat's in the Bag....mkv
S01E03 - Breaking Bad - ...And the Bag's in the River.mkv
S01E04 - Breaking Bad - Cancer Man.mkv
S01E05 - Breaking Bad - Gray Matter.mkv
S01E06 - Breaking Bad - Crazy Handful of Nothin'.mkv
S01E07 - Breaking Bad - A No-Rough-Stuff-Type Deal.mkv
Breaking Bad - S01E01.srt
Breaking Bad - S01E02.srt
Breaking Bad - S01E03.srt
Breaking Bad - S01E04.srt
Breaking Bad - S01E05.srt
Breaking Bad - S01E06.srt
Breaking Bad - S01E07.srt
```

Step 1: Open terminal in a given directory with the files you want to match subtitles to videos.

```
C:\Users\user1\series\BreakingBad>
```

Step 2: run command `python -m subs_match`

```
C:\Users\user1\series\BreakingBad> python -m subs_match
Breaking Bad - S01E01.srt -> S01E01 - Breaking Bad - Pilot.srt
Breaking Bad - S01E02.srt -> S01E02 - Breaking Bad - Cat's in the Bag....srt
Breaking Bad - S01E03.srt -> S01E03 - Breaking Bad - ...And the Bag's in the River.srt
Breaking Bad - S01E04.srt -> S01E04 - Breaking Bad - Cancer Man.srt
Breaking Bad - S01E05.srt -> S01E05 - Breaking Bad - Gray Matter.srt
Breaking Bad - S01E06.srt -> S01E06 - Breaking Bad - Crazy Handful of Nothin'.srt
Breaking Bad - S01E07.srt -> S01E07 - Breaking Bad - A No-Rough-Stuff-Type Deal.srt
7 match(es) found.
Do you wish to rename these files? [Y/n]
```

Step 3: If you agree with the matching type `y` or `Y` (or just click enter). If you don't agree type `n` or `N`.

```
...
Do you wish to rename these files? [Y/n]y
Renamed 7 file(s).
```

And that's it, your files should be renamed with the correct names.

Check out the next section for more features of this script.

## Full Usage

```
usage: subs_match [-h] [-f] [-n] [-p] [-r] [-s] [-q] [-v] [-y] [path-to-dir]

positional arguments:
  path-to-dir        path to directory where the files are, if not given uses CWD

options:
  -h, --help         show this help message and exit
  -f, --force        forces renaming/copying even if the files already have the correct name
  -n, --no-color     removes ANSI codes used for the colors.
  -p, --preserve     instead of renaming the subtitle files, they will be copied and the original files will be moved to a sub-directory
  -r, --recursive    recursively calls script on every sub-directory (matching in only done with files in the same directory)
  -s, --skip-season  ignores season numbers if it doesn't find them (instead of defaulting to season 1)
  -q, --quiet        only show errors and prompt to confirm (if flag --yes is activated the prompt won't be shown)
  -v, --verbose      also show files found and parsing results
  -y, --yes          skip confirmation prompt
```

## How to run this script in any directory

- Step 1: Add script's directory to the PYTHONPATH environment variable (create variable if it doesn't exist)
- Step 2: Run script with `python -m subs_match [args]`

By running the script like this the cwd for the script will be set to the current directory.
