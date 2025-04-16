
# Pattern Matcher for the Video Files and for the Subtitle Files
import re
class Pattern:
    IDENTIFIER_REGEX = re.compile('|'.join([
        r'[Ss]\d{1,2}[Xx]?[Ee][Pp]?\d{1,3}',
        r'\d{1,2}[Xx]\d{1,3}', # Prefer ids with season
        r'[Ee][Pp]?\d{1,3}', # Otherwise take just episode
        r'(?<![SsXx\d])\d{4}(?![p\d])', # Otherwise take a year (e.g. for movies)
        r'(?<![SsXx\d])\d+(?![p\d])', # Otherwise take the first number that appears
    ]))

    SEASON_ID_REGEX = re.compile(r'[Ss](\d{1,2})') # ONLY USED if IDENTIFIER_REGEX only found one number

    IDENTIFIER_PARSE_REGEX = re.compile(r'(?:(\d+)\D+)?(\d+)$') # To get the numbers from identifier

    class PatternId:
        def __init__(self, string, skip_season=False):
            self.string = string
            self.skip_season = skip_season
            identifier = Pattern.extract_identifier(string)
            self.id, self.id2 = Pattern.extract_ids(identifier, string, self.skip_season)

        def __lt__(self, other):
            if self.skip_season and other.skip_season: return self.id < other.id
            return self.id2 < other.id2 or (self.id2 == other.id2 and self.id < other.id)
        def __eq__(self, other):
            return self.id == other.id and ((self.skip_season and other.skip_season) or self.id2 == other.id2)
        def __hash__(self):
            if self.skip_season: return self.id
            return self.id ^ (self.id2 << 16)
        
        def __repr__(self):
            return f'PatternId(string={self.string}, id={self.id}, id2={self.id2})'
        def __str__(self):
            if self.id2 is None: return f'E{self.id}'
            return f'S{self.id2}E{self.id}'
    
    @staticmethod
    def extract_identifier(string):
        res = Pattern.IDENTIFIER_REGEX.search(string)
        if res is None: raise ValueError(f"\"{string}\" is not a valid episode name. Couldn't extract episode identifier.")
        return res.group(0)

    @staticmethod
    def extract_ids(identifier, string, skip_season=False):
        res = Pattern.IDENTIFIER_PARSE_REGEX.search(identifier)
        if res.group(2) is None: raise ValueError(f"\"{identifier}\" is not a valid identifier.")
        id1, id2 = int(res.group(2)), None if res.group(1) is None else int(res.group(1))
        if skip_season or id2 is not None: return id1, id2
        res = Pattern.SEASON_ID_REGEX.search(string)
        # Assume Season 1 if not given (or is doesn't matter for files which don't have seasons)
        return id1, (None if skip_season else 1) if res is None else int(res.group(1))

    def __init__(self, strings, skip_season=False):
        self.skip_season = skip_season
        pattern_gen = (Pattern.PatternId(string, self.skip_season) for string in strings)
        self.patterns = { pattern_id: pattern_id.string for pattern_id in pattern_gen }
        if len(self.patterns) < len(strings):
            raise ValueError("Couldn't do 1 to 1 matching of the given strings to identifiers.")
    
    def match(self, other):
        """
        Returns best matching of the most other's entries to self's entries possible
        """
        return  list(map(lambda p: (p.string, self.patterns[p]),
                    sorted(filter(lambda p: p in self.patterns, other.patterns))))

def main():

    # Parse system arguments
    import argparse
    
    parser = argparse.ArgumentParser(
        prog='subs_match',
        description='This script matches the subtitle filenames to the video filenames of a given directory.')
    parser.add_argument('path-to-dir', nargs='?', help='path to directory where the files are, if not given uses CWD')
    parser.add_argument('-f', '--force', action='store_true', help='forces renaming/copying even if the files already have the correct name')
    parser.add_argument('-n', '--no-color', action='store_true', help='removes ANSI codes used for the colors.')
    parser.add_argument('-p', '--preserve', action='store_true',
                        help='instead of renaming the subtitle files, they will be copied and the original files will be moved to a sub-directory')
    parser.add_argument('-s', '--skip-season', action='store_true',
                        help='ignores season numbers if it doesn\'t find them (instead of defaulting to season 1)')
    parser.add_argument('-q', '--quiet', action='store_true', help='only show errors. Cannot be used without the --yes flag')
    parser.add_argument('-v', '--verbose', action='store_true', help='also show files found and parsing results')
    parser.add_argument('-y', '--yes', action='store_true', help='skip confirmation prompt')

    args = vars(parser.parse_args())
    path = args['path-to-dir']
    flag_skip_season = args['skip_season']
    flag_no_color    = args['no_color']
    flag_preserve    = args['preserve']
    flag_force       = args['force']
    flag_quiet       = args['quiet']
    flag_verbose     = args['verbose']
    flag_yes         = args['yes']
    
    class tColors: # Terminal Colors (ANSI Codes)
        BLACK   = '' if flag_no_color else '\033[30m' 
        RED     = '' if flag_no_color else '\033[31m'
        GREEN   = '' if flag_no_color else '\033[32m'
        YELLOW  = '' if flag_no_color else '\033[33m'
        BLUE    = '' if flag_no_color else '\033[34m'
        MAGENTA = '' if flag_no_color else '\033[35m'
        CYAN    = '' if flag_no_color else '\033[36m'
        WHITE   = '' if flag_no_color else '\033[37m'
        UNDERLINE = '' if flag_no_color else '\033[4m'
        RESET     = '' if flag_no_color else '\033[0m'
    class colors:
        ERROR   = tColors.RED
        WARNING = tColors.YELLOW
        TITLE   = tColors.MAGENTA
        NUMBER  = tColors.CYAN
        PREV    = tColors.RED
        NEW     = tColors.GREEN
        YES     = tColors.GREEN
        NO      = tColors.RED
        RESET   = tColors.RESET

    if flag_quiet and not flag_yes:
        print(f'{colors.ERROR}Flag --quiet cannot be used without flag --yes.{colors.RESET}')
        return
    
    if flag_quiet and flag_verbose:
        print(f'{colors.ERROR}Flags --quiet and --verbose cannot be used simultaneously.{colors.RESET}')
        return

    PRESERVE_DIR = 'old_subs'

    # Set CWD to given path if given
    from os import chdir, listdir
    if path is not None:
        if flag_verbose:
            print(f'Changing to directory "{path}"')
        chdir(path)

    # Separate Video Files and Subtitle Files
    video_extensions = [
        'webm', 'mkv', 'flv', 'vob', 'ogv', 'ogg', 'rrc', 'gifv', 'mng', 'mov', 'avi', 'qt', 'wmv', 'yuv', 'rm', 'asf', 'amv', 'mp4', 'm4p',
        'm4v', 'mpg', 'mp2', 'mpeg', 'mpe', 'mpv', 'm4v', 'svi', '3gp', '3g2', 'mxf', 'roq', 'nsv', 'flv', 'f4v', 'f4p', 'f4a', 'f4b', 'mod'
    ]
    subtitle_extensions = [ ".srt", ".sub", ".ass", ".ssa", ".vtt", ".idx", ".mpl", ".dks", ".lrc", ".smi", ".usf", ".ttml", ".xml" ]
    # ".txt" removed because it's rare and causes more trouble than it's worth

    def endswithany(string, ends):
        return any(string.endswith(end) for end in ends)

    videos = [file for file in listdir() if endswithany(file, video_extensions)]
    subs = [file for file in listdir() if endswithany(file, subtitle_extensions)]

    if flag_verbose:
        print(f'{colors.TITLE}----- Videos Found -----{colors.RESET}')
        for i, video in enumerate(videos, start=1): print(f'{colors.NUMBER}{i}.{colors.RESET} {video}')
        print(f'Found {colors.NUMBER}{len(videos)}{colors.RESET} video file(s).')
        print(f'{colors.TITLE}---- Subtitles Found ----{colors.RESET}')
        for i, sub in enumerate(subs, start=1): print(f'{colors.NUMBER}{i}{colors.RESET}. {sub}')
        print(f'Found {colors.NUMBER}{len(subs)}{colors.RESET} subtitle file(s).')

    try:
        video_pattern = Pattern(videos, skip_season=flag_skip_season)
        sub_pattern = Pattern(subs, skip_season=flag_skip_season)
    except ValueError as e:
        print(e)
        return

    if flag_verbose:
        print(f'{colors.TITLE}----- Videos Parsed -----{colors.RESET}')
        for patt_id, string in video_pattern.patterns.items():
            print(f'{colors.NUMBER}{patt_id}{colors.RESET}:\t{string}')
        print(f'Parsed {colors.NUMBER}{len(video_pattern.patterns)}{colors.RESET} video file(s).')
        print(f'{colors.TITLE}---- Subtitles Parsed ----{colors.RESET}')
        for patt_id, string in sub_pattern.patterns.items():
            print(f'{colors.NUMBER}{patt_id}{colors.RESET}:\t{string}')
        print(f'Parsed {colors.NUMBER}{len(sub_pattern.patterns)}{colors.RESET} subtitle file(s).')
        print(f'{colors.TITLE}---- Matching ----{colors.RESET}')
    matching = video_pattern.match(sub_pattern)

    # Rename subtitle files to the new name
    from os.path import splitext

    # Match extensions
    def match_extension(sub, vid):
        _, ext = splitext(sub)
        name, _ = splitext(vid)
        return f'{name}{ext}'
    matching = [(sub, match_extension(sub, vid)) for sub, vid in matching]    

    # Check if files already renamed
    not_already_matching = [(sub, new_sub) for sub, new_sub in matching if sub != new_sub]
    already_matching_count = len(matching) - len(not_already_matching)
    if not flag_quiet and already_matching_count > 0:
        print(f'{colors.NUMBER}{already_matching_count}{colors.RESET} file(s) are already with the correct name.')
        if flag_force:
            action_string = 'copy' if flag_preserve else 'rename' 
            print(f'{colors.WARNING}Forcing {action_string} anyway.{colors.RESET}')
    if not flag_force:
        matching = not_already_matching
    if not flag_quiet and len(matching) > 0:
        max_len = max(len(sub) for sub, _ in matching)
        for sub, new_sub in matching:
            padding = ' ' * (max_len - len(sub))
            print(f'{colors.PREV}{sub}{colors.RESET}{padding} -> {colors.NEW}{new_sub}{colors.RESET}')
    
    if len(matching) == 0:
        if not flag_quiet: print(f'{colors.WARNING}No matches found.{colors.RESET} Exiting...')
        return
    if not flag_quiet: print(f'{colors.NUMBER}{len(matching)}{colors.RESET} match(es) found.')

    # Ask for confirmation (if flag_yes is not active)
    do_action = flag_yes
    if not flag_yes:
        for _ in range(10): # Max 10 times
            plural_str = 'this file' if len(matching) == 1 else 'these files'
            user_choice = input(f'Do you wish to rename {plural_str}? [{colors.YES}Y{colors.RESET}/{colors.NO}n{colors.RESET}]')
            if len(user_choice) <= 1 and user_choice in 'yYnN': break
            print(f'{colors.WARNING}Please type y or n.{colors.RESET}')
        if len(user_choice) > 1 or user_choice not in 'yYnN':
            print(f'{colors.ERROR}Max tries reached.{colors.RESET} Exiting...')
            return
        do_action = user_choice in 'yY' # if user_choice is empty it will default to True

    if not do_action: return

    prev_len = 0
    def print_cr(s):
        nonlocal prev_len
        padding = ' ' * max(0, prev_len - len(s))
        s = f'{s}{padding}'
        prev_len = len(s)
        print(f'\r{s}', end='')

    from os import mkdir, rename
    from os.path import exists as path_exists
    if flag_preserve: # Copy Subtitles to new file with new name
        from shutil import copyfile
        from pathlib import Path
        i = 1
        new_directory_name = PRESERVE_DIR
        while path_exists(new_directory_name):
            new_directory_name = f'{PRESERVE_DIR}{i}'
            i += 1
        mkdir(new_directory_name)
        for sub, _ in matching: # Move to new dir
            new_file_name = Path(new_directory_name) / sub
            if not flag_quiet: print_cr(f'Moving {colors.PREV}"{sub}"{colors.RESET} -> {colors.NEW}"{new_file_name}"{colors.RESET}')
            rename(sub, new_file_name)
        if not flag_quiet: print_cr(f'Moved {colors.NUMBER}{len(matching)}{colors.RESET} file(s).')
        for sub, new_sub in matching: # Copy with new name
            new_file_name = Path(new_directory_name) / sub
            if not flag_quiet: print_cr(f'Coping {colors.PREV}"{new_file_name}"{colors.RESET} -> {colors.NEW}"{new_sub}"{colors.RESET}')
            copyfile(new_file_name, new_sub)
        if not flag_quiet: print_cr(f'Copied {colors.NUMBER}{len(matching)}{colors.RESET} file(s) to directory "{new_directory_name}".')
    else: # Rename subtitles to the new name
        for sub, new_sub in matching:
            if not flag_quiet: print_cr(f'Renaming {colors.PREV}"{sub}"{colors.RESET} -> {colors.NEW}"{new_sub}"{colors.RESET}')
            rename(sub, new_sub)
        if not flag_quiet: print_cr(f'Renamed {colors.NUMBER}{len(matching)}{colors.RESET} file(s).')
    if not flag_quiet: print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nIterrupted. Exiting...')
