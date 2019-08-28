import argparse
import sys

from charset_normalizer import CharsetNormalizerMatches
from prettytable import PrettyTable


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".

    Credit goes to (c) https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def cli_detect(argv=None):
    parser = argparse.ArgumentParser(
        description="The Real First Universal Charset Detector. "
                    "Discover originating encoding used on text file. "
                    "Normalize text to unicode."
    )

    parser.add_argument('file', type=argparse.FileType('rb'), nargs='+', help='Filename')
    parser.add_argument('--verbose', action="store_true", default=False, dest='verbose',
                        help='Display complementary information about file if any.')
    parser.add_argument('--normalize', action="store_true", default=False, dest='normalize',
                        help='Permit to normalize input file. If not set, program does not write anything.')
    parser.add_argument('--replace', action="store_true", default=False, dest='replace',
                        help='Replace file when trying to normalize it instead of creating a new one.')
    parser.add_argument('--force', action="store_true", default=False, dest='force',
                        help='Replace file without asking if you are sure, use this flag with caution.')

    args = parser.parse_args(argv)

    if len(args.file) == 0:
        print('This command purpose is to analyse text file. Please specify any filename.', file=sys.stderr)
        parser.print_help(file=sys.stderr)
        return 1

    if args.replace is True and args.normalize is False:
        print('Use --replace in addition of --normalize only.', file=sys.stderr)
        return 1

    if args.force is True and args.replace is False:
        print('Use --force in addition of --replace only.', file=sys.stderr)
        return 1

    for my_file in args.file:

        matches = CharsetNormalizerMatches.from_fp(
            my_file
        )

        if len(matches) == 0:
            print('Unable to identify originating encoding for "{}".'.format(my_file.name), file=sys.stderr)
            continue

        x_ = PrettyTable(['Filename', 'Encoding', 'Language', 'Alphabets', 'Chaos', 'Coherence'])

        r_ = matches.best()
        p_ = r_.first()

        x_.add_row(
            [
                my_file.name,
                p_.encoding,
                p_.language,
                (' and ' if len(p_.alphabets) < 4 else '\n').join([el if 'and' not in el else '"{}"'.format(el) for el in p_.alphabets]),
                '{} %'.format(round(p_.chaos * 100., ndigits=3)),
                '{} %'.format(round(100. - p_.coherence * 100., ndigits=3))
            ]
        )

        if len(matches) > 1 and args.verbose:
            for el in matches:
                if el != p_:
                    x_.add_row(
                        [
                            '** ALTERNATIVE '+my_file.name+'**',
                            el.encoding,
                            el.language,
                            (' and ' if len(el.alphabets) < 4 else '\n').join([el if 'and' not in el else '"{}"'.format(el) for el in el.alphabets]),
                            '{} %'.format(round(el.chaos * 100., ndigits=3)),
                            '{} %'.format(round(100. - el.coherence * 100., ndigits=3))
                        ]
                    )

        print(x_)

        if args.verbose is True:
            print('"{}" could be also originating from {}.'.format(my_file.name, ','.join(r_.could_be_from_charset)))
            print('"{}" could be also be written in {}.'.format(my_file.name, ' or '.join(p_.languages)))

        if args.normalize is True:

            if p_.encoding.startswith('utf') is True:
                print('"{}" file does not need to be normalized, as it already came from unicode.')
                continue

            o_ = my_file.name.split('.')  # type: list[str]

            if args.replace is False:
                o_.insert(-1, p_.encoding)
            else:
                if args.force is False and query_yes_no(
                        'Are you sure to normalize "{}" by replacing it ?'.format(my_file.name), 'no') is False:
                    continue

            try:
                with open('./{}'.format('.'.join(o_)), 'w', encoding='utf-8') as fp:
                    fp.write(
                        str(p_)
                    )
            except IOError as e:
                print(str(e), file=sys.stderr)
                return 2

    return 0


if __name__ == '__main__':
    cli_detect()
