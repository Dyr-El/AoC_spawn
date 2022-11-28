from optparse import OptionParser
from os import mkdir, scandir
from pathlib import Path
import re


def parse_command_line():
    parser = OptionParser("usage: %prog [options]")
    parser.add_option(
        "-y",
        "--year",
        dest="year",
        help="the year of the created folder",
        action="store",
    )
    parser.add_option(
        "-f",
        "--force",
        dest="force",
        help="force overwriting of folder contents",
        action="store_true",
        default=False,
    )
    parser.add_option(
        "-d",
        "--directory",
        dest="directory",
        help="directory name to use (instead of the year number)",
    )
    return parser.parse_args()


def allDirectories():
    with scandir() as it:
        for entry in it:
            if entry.is_dir():
                yield entry.name


def find_next_year():
    maxNr = -1
    for directory in allDirectories():
        try:
            maxNr = max(int(directory), maxNr)
        except ValueError:
            pass
    return str(maxNr + 1)


def createDir(dir_name, year):
    mkdir(dir_name)


def copyLocalSettings(dir_name):
    loc_set_path = Path(".", "local_settings.py")
    loc_dest_path = Path(dir_name, "local_settings.py")
    with loc_set_path.open(mode="rt") as infile:
        with loc_dest_path.open(mode="wt") as outfile:
            outfile.writelines(infile.readlines())


replacements = (
    (re.compile("_YYYY-DD_"), "{year:04d}-{day:02d}"),
    (re.compile("year = "), "year = {year:d}"),
    (re.compile("day  = "), "day  = {day:d}"),
)


def modifyDayLine(line, year, day):
    replacement_data = {"year": year, "day": day}
    for repl_pattern, template_str in replacements:
        if repl_pattern.search(line):
            print(line)
            repl_str = template_str.format(replacement_data, year=year, day=day)
            return repl_pattern.sub(repl_str, line)
    return line


def copyDayFile(dir_name, year, day):
    inpath = Path(".", "DayTemplate.ipynb")
    outpath = Path(dir_name, f"Aoc_{year}_{day:02}.ipynb")
    with inpath.open(mode="rt") as infile:
        with outpath.open(mode="wt") as outfile:
            for line in infile.readlines():
                outfile.write(modifyDayLine(line, year, day))


def copyDayFiles(dir_name, year):
    for day in range(1, 26):
        copyDayFile(dir_name, year, day)
    copyLocalSettings(dir_name)


def main():
    actions = list()
    options = parse_command_line()
    if options[0].year:
        yyyy = options[0].year
        try:
            year = int(yyyy)
        except ValueError:
            print("Invalid year given")
            return
    else:
        yyyy = find_next_year()
        year = int(yyyy)
    if options[0].directory:
        dirName = options[0].directory
    else:
        dirName = yyyy
    if any((dirName == dname for dname in allDirectories())):
        print(f"Directory ./{yyyy}/ does already exist!")
        if options[0].force:
            print("  Files in it will be overwritten")
        else:
            print("  Use option --force to force an overwrite.")
            return
    else:
        actions.append(createDir)
    actions.append(copyDayFiles)
    for action in actions:
        if isinstance(action, str):
            print(f"Fake doing action [{action}({dirName}, {year})]")
        else:
            action(dirName, year)


if __name__ == "__main__":
    main()
