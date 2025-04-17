
# Pattern Matcher for the Video Files and for the Subtitle Files
from re import compile as regex_compile
class Pattern:
    IDENTIFIER_REGEXS = [ # Common season and episode identifiers
        regex_compile(r'(?<![a-zA-Z\d])[Ss](\d{1,2})[Xx]?[Ee][Pp]?(\d{1,4})(?!\d)'),
        regex_compile(r'(?<![a-zA-Z\d])(\d{1,2})[Xx](\d{1,4})(?![a-zA-Z\d])'),
    ]

    SEASON_REGEXS = [
        regex_compile(r'(?<![a-zA-Z\d])[Ss](\d{1,2})(?![a-zA-Z\d])'),
        regex_compile(r'(?<![a-zA-Z\d])[Ss][Ee][Aa][Ss][Oo][Nn][^a-zA-Z\d]?(\d{1,2})(?!\d)'),
    ]

    EPISODE_REGEXS = [
        regex_compile(r'(?<![a-zA-Z\d])[Ee][Pp]?(\d{1,4})(?![a-zA-Z\d])'),
        regex_compile(r'(?<![a-zA-Z\d])[Ee][Pp][Ii][Ss][Oo][Dd][Ee][^a-zA-Z\d]?(\d{1,4})(?!\d)'),
    ]

    NUMBER_REGEXS = [
        regex_compile(r'(?<![a-zA-Z\d])(\d{1,3})(?![a-zA-Z\d])'), # Take episode number
        regex_compile(r'(?<![a-zA-Z\d])(\d{4})(?![a-zA-Z\d])'), # Otherwise take a year (e.g. for movies)
        regex_compile(r'(?<![a-zA-Z\d])(\d{5,})(?![a-zA-Z\d])'), # Otherwise take the first number that appears
    ]

    class PatternId:
        def __init__(self, string, skip_season=False):
            self.string = string
            self.season, self.episode = Pattern.extract_season_episode(string, skip_season)

        def get_key(self):
            return (self.season, self.episode)

        def __lt__(self, other):
            return self.season < other.season or (self.season == other.season and self.episode < other.episode)
        def __eq__(self, other):
            return self.episode == other.episode and self.season == other.season
        def __hash__(self):
            if self.season < 0: return self.episode
            return self.episode ^ (self.season << 16)
        
        def __repr__(self):
            return f'PatternId(string={self.string}, episode={self.episode}, season={self.season})'
        def __str__(self):
            return Pattern.PatternId.key2str(self.season, self.episode)
        @staticmethod
        def key2str(season, episode):
            if season < 0: return f'E{episode}'
            return f'S{season}E{episode}'
    
    @staticmethod
    def extract_season_episode(string, skip_season=False):
        SKIP_SEASON_VALUE = -1
        for regex in Pattern.IDENTIFIER_REGEXS:
            res = regex.search(string)
            if res is not None:
                return SKIP_SEASON_VALUE if skip_season else int(res.group(1)), int(res.group(2))
        episode_res = None
        for regex in Pattern.EPISODE_REGEXS:
            episode_res = regex.search(string)
            if episode_res is not None: break
        # Return if already found epside and don't need season
        if skip_season and episode_res is not None: return SKIP_SEASON_VALUE, int(episode_res.group(1))

        season_res = None
        season_regex = None
        for regex in Pattern.SEASON_REGEXS:
            season_res = regex.search(string)
            if season_res is not None:
                season_regex = regex
                break

        # Return if found already have episode number (assume season 1 if not found)
        if not skip_season and episode_res is not None:
            return 1 if season_res is None else int(season_res.group(1)), int(episode_res.group(1))

        # Remove season number if found
        original_string = string
        if season_res is not None:
            string = season_regex.sub('', string)
        
        # Find first number as episode number
        episode_res = None
        for regex in Pattern.NUMBER_REGEXS:
            episode_res = regex.search(string)
            if episode_res is not None: break
        if episode_res is None:
            raise ValueError(f'"{original_string}" parsing failed. Couldn\'t extract episode number successfully.')
        if skip_season: return SKIP_SEASON_VALUE, int(episode_res.group(1))
        if season_res is None: return 1, int(episode_res.group(1)) # Assume season 1
        return int(season_res.group(1)), int(episode_res.group(1))

    def __init__(self, strings, skip_season=False):
        self.skip_season = skip_season
        pattern_list = [ Pattern.PatternId(string, self.skip_season) for string in strings ]
        self.patterns = { pattern_id.get_key(): [] for pattern_id in pattern_list } # eliminates repeated ids
        for pattern_id in pattern_list:
            self.patterns[pattern_id.get_key()].append(pattern_id.string)

    def match(self, other):
        """
        Returns best matching of the most other's entries to self's entries possible
        """
        return  list(map(lambda key: (other.patterns[key][0], self.patterns[key][0]),
                    sorted(filter(lambda key: key in self.patterns, other.patterns))))

VIDEO_EXTENSIONS = [
    'webm', 'mkv', 'flv', 'vob', 'ogv', 'ogg', 'rrc', 'gifv', 'mng', 'mov', 'avi', 'qt', 'wmv', 'yuv', 'rm', 'asf', 'amv', 'mp4', 'm4p',
    'm4v', 'mpg', 'mp2', 'mpeg', 'mpe', 'mpv', 'm4v', 'svi', '3gp', '3g2', 'mxf', 'roq', 'nsv', 'flv', 'f4v', 'f4p', 'f4a', 'f4b', 'mod'
]
SUBTITLE_EXTENSIONS = [ ".srt", ".sub", ".ass", ".ssa", ".vtt", ".idx", ".mpl", ".dks", ".lrc", ".smi", ".usf", ".ttml", ".xml" ]
# ".txt" removed because it's rare and causes more trouble than it's worth

PRESERVE_DIRECTORY = '(subs_match)old_subs'

class FLAGS:
    NONE        = 0b00000000
    NO_COLOR    = 0b00000001
    FORCE       = 0b00000010
    PRESERVE    = 0b00000100
    RECURSIVE   = 0b00001000
    SKIP_SEASON = 0b00010000
    QUIET       = 0b00100000
    VERBOSE     = 0b01000000
    YES         = 0b10000000

class TERMINAL_COLORS: # ANSI Codes
    BLACK   = '\033[30m' 
    RED     = '\033[31m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    BLUE    = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN    = '\033[36m'
    WHITE   = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET     = '\033[0m'

from os import chdir, getcwd, listdir, mkdir, rename
from os.path import isfile as path_isfile, isdir as path_isdir, splitext

from shutil import copyfile
from pathlib import Path

def match_directory(path=None, flags=FLAGS.NONE):
    flag_no_color    = bool(flags & FLAGS.NO_COLOR)
    flag_quiet       = bool(flags & FLAGS.QUIET)
    flag_verbose     = bool(flags & FLAGS.VERBOSE)
    flag_yes         = bool(flags & FLAGS.YES)

    class colors:
        ERROR   = '' if flag_no_color else TERMINAL_COLORS.RED
        WARNING = '' if flag_no_color else TERMINAL_COLORS.YELLOW
        TITLE   = '' if flag_no_color else TERMINAL_COLORS.MAGENTA
        NUMBER  = '' if flag_no_color else TERMINAL_COLORS.CYAN
        PATH    = '' if flag_no_color else TERMINAL_COLORS.BLUE
        PREV    = '' if flag_no_color else TERMINAL_COLORS.RED
        NEW     = '' if flag_no_color else TERMINAL_COLORS.GREEN
        YES     = '' if flag_no_color else TERMINAL_COLORS.GREEN
        NO      = '' if flag_no_color else TERMINAL_COLORS.RED
        RESET   = '' if flag_no_color else TERMINAL_COLORS.RESET
    
    if flag_quiet and flag_verbose:
        print(f'{colors.ERROR}Flags --quiet and --verbose cannot be used simultaneously.{colors.RESET}')
        return

    # Set CWD to given path if given
    if path is not None:
        chdir(path)
    _match_directory(colors, flags=flags)


def _match_directory(colors, flags=FLAGS.NONE):
    flag_force       = bool(flags & FLAGS.FORCE)
    flag_preserve    = bool(flags & FLAGS.PRESERVE)
    flag_recursive   = bool(flags & FLAGS.RECURSIVE)
    flag_skip_season = bool(flags & FLAGS.SKIP_SEASON)
    flag_quiet       = bool(flags & FLAGS.QUIET)
    flag_verbose     = bool(flags & FLAGS.VERBOSE)
    flag_yes         = bool(flags & FLAGS.YES)

    current_directory = listdir()
    action_name_string = 'move and copy' if flag_preserve else 'rename' 

    # Recusively call _match_directory on sub_directories
    if flag_recursive:
        for directory in filter(path_isdir, current_directory):
            chdir(directory)
            _match_directory(colors, flags=flags)
            chdir('./..')

    if flag_verbose:
        print(f'Matching in {colors.PATH}"{getcwd()}"{colors.RESET}')
    elif not flag_quiet and flag_recursive:
        print(f'{colors.PATH}"{getcwd()}"{colors.RESET}:')

    # Separate Video Files and Subtitle Files
    def endswithany(string, ends):
        return any(string.endswith(end) for end in ends)

    videos = [file for file in current_directory if path_isfile(file) and endswithany(file, VIDEO_EXTENSIONS)]
    subs = [file for file in current_directory if path_isfile(file) and endswithany(file, SUBTITLE_EXTENSIONS)]

    if flag_verbose:
        print(f'{colors.TITLE}----- Videos Found -----{colors.RESET}')
        for i, video in enumerate(videos, start=1): print(f'{colors.NUMBER}{i}.{colors.RESET}\t{video}')
        print(f'Found {colors.NUMBER}{len(videos)}{colors.RESET} video file(s).')
        print(f'{colors.TITLE}---- Subtitles Found ----{colors.RESET}')
        for i, sub in enumerate(subs, start=1): print(f'{colors.NUMBER}{i}{colors.RESET}.\t{sub}')
        print(f'Found {colors.NUMBER}{len(subs)}{colors.RESET} subtitle file(s).')
    elif not flag_quiet:
        print(f'Found {colors.NUMBER}{len(videos)}{colors.RESET} video file(s).')
        print(f'Found {colors.NUMBER}{len(subs)}{colors.RESET} subtitle file(s).')
    if len(videos) == 0 or len(subs) == 0:
        if not flag_quiet: print(f'{colors.WARNING}No files to match.{colors.RESET} Exiting...')
        return
    try:
        video_pattern = Pattern(videos, skip_season=flag_skip_season)
        sub_pattern = Pattern(subs, skip_season=flag_skip_season)
    except ValueError as e:
        print(f'{colors.ERROR}{e}{colors.RESET}')
        return
    
    not_one_to_one_match_video = len(video_pattern.patterns) != len(videos)
    not_one_to_one_match_subs = len(sub_pattern.patterns) != len(subs)
    if (not_one_to_one_match_video or not_one_to_one_match_subs) and flag_yes:
        print(f'{colors.ERROR}Couldn\'t do a 1 to 1 matching. Please run without the --yes flag.{colors.RESET}')
        return
    
    if flag_verbose or not_one_to_one_match_video:
        print(f'{colors.TITLE}----- Videos Parsed -----{colors.RESET}')
        for patt_id, strings in video_pattern.patterns.items():
            patt_id = Pattern.PatternId.key2str(*patt_id)
            for i, string in enumerate(strings):
                header = f'{colors.NUMBER}{patt_id}{colors.RESET}:' if i == 0 else (' ' * (len(patt_id) + 1))
                print(f'{header}\t{string}')
        print(f'Parsed {colors.NUMBER}{len(videos)}{colors.RESET} video file(s).')
    if not_one_to_one_match_video:
        print(f'{colors.WARNING}Couldn\'t do a 1 to 1 matching on videos. Taking the first option(s).{colors.RESET}')
    
    if flag_verbose or not_one_to_one_match_subs:
        print(f'{colors.TITLE}---- Subtitles Parsed ----{colors.RESET}')
        for patt_id, strings in sub_pattern.patterns.items():
            patt_id = Pattern.PatternId.key2str(*patt_id)
            for i, string in enumerate(strings):
                header = f'{colors.NUMBER}{patt_id}{colors.RESET}:' if i == 0 else (' ' * (len(patt_id) + 1))
                print(f'{header}\t{string}')
        print(f'Parsed {colors.NUMBER}{len(subs)}{colors.RESET} subtitle file(s).')
    if not_one_to_one_match_subs:
        print(f'{colors.WARNING}Couldn\'t do a 1 to 1 matching on subs. Taking the first option(s).{colors.RESET}')

    if flag_verbose:
        print(f'{colors.TITLE}---- Matching ----{colors.RESET}')
        print(f'{colors.PATH}"{getcwd()}"{colors.RESET}:')
    matching = video_pattern.match(sub_pattern)

    # Rename subtitle files to the new name

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
            print(f'{colors.WARNING}Forcing {action_name_string} anyway.{colors.RESET}')
    if not flag_force:
        matching = not_already_matching.copy()
    
    # Check if new file names are available
    for sub, new_sub in not_already_matching:
        if path_isfile(new_sub):
            if flag_quiet:
                print(f'{colors.ERROR}Not all new subtitle names are not available. Please run without the --quiet flag.{colors.RESET}')
            print(f'{colors.WARNING}Filename {colors.RESET}"{new_sub}"{colors.WARNING} is not available. Removing it from matches.{colors.RESET}')
            matching.remove((sub, new_sub))
    
    # Print matching results (it's printed even with flag_quiet if need for the prompt)
    if not (flag_quiet and flag_yes) and len(matching) > 0:
        if flag_quiet and flag_recursive: # Print path for clarity with quiet recursive calls
            print(f'{colors.PATH}"{getcwd()}"{colors.RESET}:')
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
        MAX_TRIES = 10
        for _ in range(MAX_TRIES): # Max 10 times
            plural_str = 'this file' if len(matching) == 1 else 'these files'
            user_choice = input(f'Do you wish to {action_name_string} {plural_str}? [{colors.YES}Y{colors.RESET}/{colors.NO}n{colors.RESET}]')
            if len(user_choice) <= 1 and user_choice in 'yYnN': break
            print(f'{colors.WARNING}Please type y or n.{colors.RESET}')
        if len(user_choice) > 1 or user_choice not in 'yYnN':
            print(f'{colors.ERROR}Maximum of {MAX_TRIES} tries reached.{colors.RESET} Exiting...')
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

    if flag_preserve: # Copy Subtitles to new file with new name
        i = 1
        new_directory_name = PRESERVE_DIRECTORY
        while path_isdir(new_directory_name):
            new_directory_name = f'{PRESERVE_DIRECTORY}{i}'
            i += 1
        mkdir(new_directory_name)
        for sub, _ in matching: # Move to new dir
            new_file_name = Path(new_directory_name) / sub
            if not (flag_quiet and flag_yes): print_cr(f'Moving {colors.PREV}"{sub}"{colors.RESET} -> {colors.NEW}"{new_file_name}"{colors.RESET}')
            rename(sub, new_file_name)
        if not (flag_quiet and flag_yes):
            print_cr(f'Moved {colors.NUMBER}{len(matching)}{colors.RESET} file(s) to directory {colors.PATH}"{new_directory_name}"{colors.RESET}.')
            print()
        for sub, new_sub in matching: # Copy with new name
            new_file_name = Path(new_directory_name) / sub
            if not (flag_quiet and flag_yes): print_cr(f'Coping {colors.PREV}"{new_file_name}"{colors.RESET} -> {colors.NEW}"{new_sub}"{colors.RESET}')
            copyfile(new_file_name, new_sub)
        if not (flag_quiet and flag_yes): print_cr(f'Copied {colors.NUMBER}{len(matching)}{colors.RESET} file(s) from directory {colors.PATH}"{new_directory_name}"{colors.RESET}.')
    else: # Rename subtitles to the new name
        for sub, new_sub in matching:
            if not (flag_quiet and flag_yes): print_cr(f'Renaming {colors.PREV}"{sub}"{colors.RESET} -> {colors.NEW}"{new_sub}"{colors.RESET}')
            rename(sub, new_sub)
        if not (flag_quiet and flag_yes): print_cr(f'Renamed {colors.NUMBER}{len(matching)}{colors.RESET} file(s).')
    if not (flag_quiet and flag_yes): print()

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
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='recursively calls script on every sub-directory (matching in only done with files in the same directory)')
    parser.add_argument('-s', '--skip-season', action='store_true',
                        help='ignores season numbers if it doesn\'t find them (instead of defaulting to season 1)')
    parser.add_argument('-q', '--quiet', action='store_true', help='only show errors and prompt to confirm (if flag --yes is activated the prompt won\'t be shown)')
    parser.add_argument('-v', '--verbose', action='store_true', help='also show files found and parsing results')
    parser.add_argument('-y', '--yes', action='store_true', help='skip confirmation prompt')

    args = vars(parser.parse_args())
    path = args['path-to-dir']
    flags = FLAGS.NONE
    if args['no_color']:    flags |= FLAGS.NO_COLOR
    if args['force']:       flags |= FLAGS.FORCE
    if args['preserve']:    flags |= FLAGS.PRESERVE
    if args['recursive']:   flags |= FLAGS.RECURSIVE
    if args['skip_season']: flags |= FLAGS.SKIP_SEASON
    if args['quiet']:       flags |= FLAGS.QUIET
    if args['verbose']:     flags |= FLAGS.VERBOSE
    if args['yes']:         flags |= FLAGS.YES
    
    match_directory(path=path, flags=flags)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nIterrupted. Exiting...')
