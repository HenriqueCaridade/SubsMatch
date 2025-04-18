# Subs Match

This script matches the subtitle filenames to the video filenames of a given directory.

## Index
1. [Releases](#releases)
1. [Usage](#usage)
1. [Full Usage](#full-usage)
1. [How to run this script](#how-to-run-this-script) 
1. [How to run this script from any directory](#how-to-run-this-script-from-any-directory)

## Releases

There are available executable releases for every platform on the releases tab.

These executables where compiled using [pyinstaller](https://github.com/pyinstaller/pyinstaller).

## Usage

Step 0: If you didn't add the executable to PATH or the python script to PYTHONPATH as described below, copy the executable for your machine OS from releases or copy the python script from the repository into the diretory.
More information on the [How to run this script](#how-to-run-this-script) section.

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

Step 2: run command `python -m subs_match` or just `subs_match`

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

## How to run this script

This section is how to run this script for a **one time use**. If you want this script to always be available in your console, please refer to [How to run this script from any directory](#how-to-run-this-script-from-any-directory) section.

### With compiled executable

- Step 1: Go the the release pages and download the correct executable for your OS.
- Step 2: Move it to the directory with the files you want to match.
- Step 3: Open cmd and change to the correct directory `cd path/to/your/directory`
- Step 4: Run script on the cmd with `subs_match [args]`.

### With python script

**Note:** to run this script you need to install [python](https://www.python.org/downloads/) in your system, if you don't already have it.

- Step 1: Download python script from the repository.
- Step 2: Move it to the directory with the files you want to match.
- Step 3: Open cmd and change to the correct directory `cd path/to/your/directory`
- Step 4: Run script with `python subs_match.py [args]` or `python -m subs_match [args]` (if on linux please run with `python3` instead of just `python`)


## How to run this script from any directory

This section is about how to add this script to your enviroment variables to make it available from any directory. If you simply want to run a single time, please refer to [How to run this script](#how-to-run-this-script) section.

### With compiled executable

- Step 1: Go the the release pages and download the correct executable for your OS.
- Step 2: Save it in a safe directory and copy it's path.
- Step 3: Add that path to the PATH enviroment variable.
- Step 4: Run on the cmd with `subs_match [args]`.

### With python script

**Note:** to run this script you need to install [python](https://www.python.org/downloads/) in your system, if you don't already have it.

- Step 1: Download python script from the repository.
- Step 2: Save it in a safe directory and copy it's path.
- Step 3: Add that path to the PYTHONPATH environment variable (create variable if it doesn't exist)
- Step 4: Run script with `python -m subs_match [args]` (if on linux please run with `python3` instead of just `python`)

