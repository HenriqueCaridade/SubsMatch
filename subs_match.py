
# Pattern Matcher for the Video Files and for the Subtitle Files
import re

class Pattern:
    IDENTIFIER_REGEX = re.compile('|'.join([
        r'[Ss]\d{1,2}[Xx]?[Ee][Pp]?\d{1,3}',
        r'\d{1,2}[Xx]\d{1,3}', # Prefer ids with season
        r'[Ee][Pp]?\d{1,3}', # Otherwise take just episode
        r'(?<![SsXx\d])\d{4}(?!p)', # Otherwise take a year (e.g. for movies)
        r'(?<![SsXx\d])\d+(?!p)', # Otherwise take the first number that appears
    ]))

    SEASON_ID_REGEX = re.compile(r'[Ss](\d{1,2})') # ONLY USED if IDENTIFIER_REGEX only found one number

    IDENTIFIER_PARSE_REGEX = re.compile(r'(?:(\d+)\D+)?(\d+)$') # To get the numbers from identifier

    class PatternId:
        def __init__(self, string):
            self.string = string
            identifier = Pattern.extract_identifier(string)
            self.id, self.id2 = Pattern.extract_ids(identifier, string)

        def __lt__(self, other):
            return self.id2 < other.id2 or (self.id2 == other.id2 and self.id < other.id)
        def __eq__(self, other):
            return self.id == other.id and self.id2 == other.id2
        def __hash__(self):
            return self.id ^ (self.id2 << 16)
        
        def __repr__(self):
            return f'PatternId(string={self.string}, id={self.id}, id2={self.id2})'
        def __str__(self):
            if self.id2 is None: return f'{self.id}'
            return f'S{self.id2}E{self.id}'
    
    @staticmethod
    def extract_identifier(string):
        res = Pattern.IDENTIFIER_REGEX.search(string)
        if res is None: raise ValueError(f"\"{string}\" is not a valid episode name. Couldn't extract episode identifier.")
        return res.group(0)

    @staticmethod
    def extract_ids(identifier, string):
        res = Pattern.IDENTIFIER_PARSE_REGEX.search(identifier)
        if res.group(2) is None: raise ValueError(f"\"{identifier}\" is not a valid identifier.")
        id1, id2 = int(res.group(2)), None if res.group(1) is None else int(res.group(1))
        if id2 is not None: return id1, id2
        res = Pattern.SEASON_ID_REGEX.search(string)
        # Assume Season 1 if not given (or is doesn't matter for files which don't have seasons)
        return id1, 1 if res is None else int(res.group(1))

    def __init__(self, strings):
        pattern_gen = (Pattern.PatternId(string) for string in strings)
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
    parser.add_argument('-p', '--preserve', action='store_true',
                        help='instead of renaming the subtitle files, they will be copied and the original files will be moved to a sub-directory')
    parser.add_argument('-f', '--force', action='store_true', help='force rename/copy (i.e. no confirmation prompt)')

    args = vars(parser.parse_args())
    path = args['path-to-dir']
    preserve_flag = args['preserve']
    force_flag = args['force']

    PRESERVE_DIR = 'old_subs'

    from os import chdir, listdir
    # Set CWD to given path if given
    if path is not None:
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

    video_pattern = Pattern(videos)
    sub_pattern = Pattern(subs)
    matching = video_pattern.match(sub_pattern)

    # Rename subtitle files to the new name
    from os.path import splitext

    # Match extensions
    def match_extension(sub, vid):
        _, ext = splitext(sub)
        name, _ = splitext(vid)
        return f'{name}{ext}'
    matching = [(sub, match_extension(sub, vid)) for sub, vid in matching]    

    # Ask for confirmation (if force_flag is not active)
    do_action = force_flag
    if not force_flag:
        for sub, new_sub in matching:
            print(sub, '\t->', new_sub)
        while True:
            user_choice = input("Do you wish to rename this files? [Y/n]")
            if len(user_choice) <= 1 and user_choice in 'yYnN': break
        do_action = len(user_choice) == 0 or user_choice in 'yY'

    from os import mkdir, rename
    from os.path import exists as path_exists
    if do_action:
        if preserve_flag: # Copy Subtitles to new file with new name
            from shutil import copyfile
            from pathlib import Path
            i = 1
            new_directory_name = PRESERVE_DIR
            while path_exists(new_directory_name):
                new_directory_name = f'{PRESERVE_DIR}{i}'
                i += 1
            mkdir(new_directory_name)
            for sub, _ in matching: # Move to new dir
                rename(sub, Path(new_directory_name) / sub)
            for sub, new_sub in matching: # Copy with new name
                copyfile(Path(new_directory_name) / sub, new_sub)
        else: # Rename subtitles to the new name
            for sub, new_sub in matching:
                rename(sub, new_sub)

if __name__ == "__main__":
    main()
