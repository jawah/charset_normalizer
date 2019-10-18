from loguru import logger

from charset_normalizer.normalizer import CharsetNormalizerMatches as CnM
from chardet import detect as chardet_detect
from cchardet import detect as cchardet_detect

from charset_normalizer.version import __version__ as charset_normalizer_ver
from chardet import __version__ as chardet_version
from cchardet import __version__ as cchardet_version

from time import perf_counter_ns, sleep
from prettytable import PrettyTable
from encodings.aliases import aliases

from os.path import basename
from glob import glob
from statistics import mean

from difflib import SequenceMatcher

report = {

    'chardet': {
        'success': 0,
        'failure': 0,
        'performances': list(),
        'similarities_in_failures': list(),
        'encodings': dict()
    },

    'cchardet': {
        'success': 0,
        'failure': 0,
        'performances': list(),
        'similarities_in_failures': list(),
        'encodings': dict()
    },

    'charset-normalizer': {
        'success': 0,
        'failure': 0,
        'performances': list(),
        'similarities_in_failures': list(),
        'encodings': dict()
    },

}


def also_could_be(encoding):
    if encoding == 'uhc':  # for cchardet. UHC ==> EUC_KR
        return 'euc_kr'
    if 'sig' in encoding:
        encoding = encoding.replace('_sig', '')
    for a, b in aliases.items():
        if a == encoding:
            return b
    return encoding


def does_it_matter(raw_bytes, detected_encoding, should_be_encoding):
    """
    :param bytes raw_bytes:
    :param str detected_encoding:
    :param str should_be_encoding:
    :return:
    """
    if detected_encoding == should_be_encoding:
        return False
    if detected_encoding == 'UHC' and should_be_encoding == 'cp949':
        return False
    try:
        return raw_bytes.decode(detected_encoding) != raw_bytes.decode(should_be_encoding)
    except UnicodeDecodeError:
        return True


def how_far_for_expected_result(raw_bytes, detected_encoding, should_be_encoding):
    if detected_encoding == should_be_encoding:
        return 0.

    t_original = raw_bytes.decode(should_be_encoding)

    try:
        t1_tempered = raw_bytes.decode(detected_encoding)
    except UnicodeDecodeError:
        return 100.

    m = SequenceMatcher(None, t_original, t1_tempered)

    return round(
        m.ratio() * 100,
        ndigits=3
    )


if __name__ == '__main__':

    logger.warning(
        "Running feature benchmark on charset-normalizer ({v1}), chardet ({v2}) and cchardet ({v3}).",
        v1=charset_normalizer_ver,
        v2=chardet_version,
        v3=cchardet_version
    )

    files_queue = glob('../data/chardet/**/*')

    for path in files_queue:

        target_encoding_dir = path.split('/')[-2].lower().replace('-', '_')

        if target_encoding_dir.startswith('windows_'):
            target_encoding_dir = '_'.join(target_encoding_dir.split('_')[:2])
        if target_encoding_dir.startswith('iso'):
            target_encoding_dir = 'iso{n1}_{n2}'.format(n1=target_encoding_dir.split('_')[1],
                                                        n2=target_encoding_dir.split('_')[2])
        if 'sig' in target_encoding_dir:
            target_encoding_dir = target_encoding_dir.replace('_sig', '')

        should_be_encoding = None

        for a, b in aliases.items():
            if a == target_encoding_dir:
                should_be_encoding = b
                break
            elif b == target_encoding_dir:
                should_be_encoding = target_encoding_dir
                break

        if should_be_encoding is None:
            logger.warning(
                '{encoding} could not be identified in encodings.aliases. '
                'So "{filename}" is going to be ignored.',
                encoding=target_encoding_dir,
                filename=basename(path)
            )
            continue

        if should_be_encoding not in report['charset-normalizer']['encodings'].keys():
            for competitor in report.keys():
                report[competitor]['encodings'][should_be_encoding] = {
                    'performances': list(),
                    'success': 0,
                    'failure': 0,
                    'confuse_it_with': set(),
                    'similarities_in_failures': list()
                }

        logger.info('File "{filename}" is going to be tested. File owner claim it is encoded with {target_encoding}.', filename=basename(path), target_encoding=should_be_encoding)

        before_reading_file = perf_counter_ns()

        raw_content = open(path, 'rb').read()

        after_reading_file = perf_counter_ns()

        logger.info('"{filename}" was loaded within {ts} nanoseconds.', filename=basename(path), ts=(after_reading_file-before_reading_file))

        before_chardet_decide = perf_counter_ns()

        chardet_result = chardet_detect(raw_content)

        after_chardet_decide = perf_counter_ns()

        logger.info('"{filename}" content was identified within {ts} nanoseconds by CHARDET.', filename=basename(path),
                    ts=(after_chardet_decide - before_chardet_decide))

        report['chardet']['performances'].append(after_chardet_decide - before_chardet_decide)
        report['chardet']['encodings'][should_be_encoding]['performances'].append(after_chardet_decide - before_chardet_decide)

        if chardet_result.get('encoding') is None:
            logger.warning('"{filename}" content could not identified by CHARDET.')
            report['chardet']['failure'] += 1
            report['chardet']['encodings'][should_be_encoding]['failure'] += 1
        elif should_be_encoding != also_could_be(chardet_result.get('encoding').lower().replace('-', '_')) and does_it_matter(raw_content, should_be_encoding, also_could_be(chardet_result.get('encoding').lower().replace('-', '_'))) is True:

            similarity_to_expected_result = how_far_for_expected_result(raw_content, chardet_result.get('encoding').replace('-', '_'), should_be_encoding)

            logger.error(
                '"{filename}" content could not identified properly by CHARDET. ({got} instead of {should_be}). '
                '{percent_far_from_original} % is rendered correctly thought.',
                filename=basename(path),
                got=chardet_result.get('encoding').replace('-', '_'),
                should_be=should_be_encoding,
                percent_far_from_original=similarity_to_expected_result
            )

            report['chardet']['failure'] += 1
            report['chardet']['similarities_in_failures'].append(similarity_to_expected_result)

            report['chardet']['encodings'][should_be_encoding]['failure'] += 1
            report['chardet']['encodings'][should_be_encoding]['similarities_in_failures'].append(similarity_to_expected_result)
            report['chardet']['encodings'][should_be_encoding]['confuse_it_with'].add(
                also_could_be(chardet_result.get('encoding').lower().replace('-', '_')))


        else:
            report['chardet']['success'] += 1
            report['chardet']['encodings'][should_be_encoding]['success'] += 1

        before_cchardet_decide = perf_counter_ns()

        cchardet_result = cchardet_detect(raw_content)

        after_cchardet_decide = perf_counter_ns()

        logger.info('"{filename}" content was identified within {ts} nanoseconds by CCHARDET.', filename=basename(path),
                    ts=(after_cchardet_decide - before_cchardet_decide))

        report['cchardet']['performances'].append(after_cchardet_decide - before_cchardet_decide)
        report['cchardet']['encodings'][should_be_encoding]['performances'].append(
            after_cchardet_decide - before_cchardet_decide)

        if cchardet_result.get('encoding') is None:
            logger.warning('"{filename}" content could not identified by CCHARDET.')
            report['cchardet']['failure'] += 1
            report['cchardet']['encodings'][should_be_encoding]['failure'] += 1
        elif should_be_encoding != also_could_be(cchardet_result.get('encoding').lower().replace('-', '_')) and does_it_matter(raw_content, should_be_encoding, also_could_be(cchardet_result.get('encoding').lower().replace('-', '_'))) is True:

            similarity_to_expected_result = how_far_for_expected_result(raw_content, cchardet_result.get('encoding').replace('-', '_'), should_be_encoding)

            logger.error(
                '"{filename}" content could not identified properly by CCHARDET. ({got} instead of {should_be}). '
                '{percent_far_from_original} % is rendered correctly thought.',
                filename=basename(path),
                got=cchardet_result.get('encoding').replace('-', '_'),
                should_be=should_be_encoding,
                percent_far_from_original=similarity_to_expected_result
            )

            report['cchardet']['failure'] += 1
            report['cchardet']['similarities_in_failures'].append(similarity_to_expected_result)

            report['cchardet']['encodings'][should_be_encoding]['failure'] += 1
            report['cchardet']['encodings'][should_be_encoding]['similarities_in_failures'].append(similarity_to_expected_result)

            report['cchardet']['encodings'][should_be_encoding]['confuse_it_with'].add(
                also_could_be(cchardet_result.get('encoding').lower().replace('-', '_')))
        else:
            report['cchardet']['success'] += 1
            report['cchardet']['encodings'][should_be_encoding]['success'] += 1

        before_cn_decide = perf_counter_ns()

        cn_result = CnM.from_bytes(raw_content).best().first()

        after_cn_decide = perf_counter_ns()

        logger.info('"{filename}" content was identified within {ts} nanoseconds by CHARSET-NORMALIZER.', filename=basename(path),
                    ts=(after_cn_decide - before_cn_decide))

        report['charset-normalizer']['performances'].append(after_cn_decide - before_cn_decide)
        report['charset-normalizer']['encodings'][should_be_encoding]['performances'].append(
            after_cn_decide - before_cn_decide)

        if cn_result is None:
            logger.warning('"{filename}" content could not identified by CHARSET-NORMALIZER.', filename=basename(path))
            report['charset-normalizer']['failure'] += 1
            report['charset-normalizer']['encodings'][should_be_encoding]['failure'] += 1
        elif should_be_encoding not in ' '.join(cn_result.could_be_from_charset):

            similarity_to_expected_result = how_far_for_expected_result(raw_content, cn_result.encoding, should_be_encoding)

            logger.error(
                '"{filename}" content could not identified properly by CHARSET-NORMALIZER. ({got} instead of {should_be}). '
                '{percent_far_from_original} % is rendered correctly thought.',
                filename=basename(path),
                got=cn_result.encoding,
                should_be=should_be_encoding,
                percent_far_from_original=similarity_to_expected_result
            )

            report['charset-normalizer']['failure'] += 1
            report['charset-normalizer']['similarities_in_failures'].append(similarity_to_expected_result)

            report['charset-normalizer']['encodings'][should_be_encoding]['failure'] += 1
            report['charset-normalizer']['encodings'][should_be_encoding]['similarities_in_failures'].append(similarity_to_expected_result)

            report['charset-normalizer']['encodings'][should_be_encoding]['confuse_it_with'].add(
                cn_result.encoding)
        else:
            report['charset-normalizer']['success'] += 1
            report['charset-normalizer']['encodings'][should_be_encoding]['success'] += 1

    # Publish result
    logger.info('Publishing results')

    sleep(0.5)

    x = PrettyTable(
        [
            'Package',
            'Accuracy',
            'Similarities in confusion',
            'Mean per file (ns)',
            'File per sec (est)'
        ]
    )

    for package in report.keys():

        mean_perf_ns = round(
            mean(
                report[package]['performances']
            )
        )

        x.add_row(
            [
                package,
                round(
                    (report[package]['success'] / (report[package]['success'] + report[package]['failure'])) * 100,
                    ndigits=2
                ),
                round(
                    mean(
                        report[package]['similarities_in_failures']
                    ),
                    ndigits=3
                ) if len(report[package]['similarities_in_failures']) > 0 else 'N/A',
                mean_perf_ns,
                round(
                    1. / (mean_perf_ns / 1e+9),
                    ndigits=3
                )
            ]
        )

    print(
        x
    )

    for encoding in report['charset-normalizer']['encodings'].keys():

        print('##', encoding.upper())

        y = PrettyTable(
            [
                'Package',
                'Accuracy',
                'Similarities in confusion',
                'Mean per file (ns)',
                'File per sec (est)',
                'Confuse it with (sometime)'
            ]
        )

        for package in report.keys():
            mean_perf_ns = round(
                mean(
                    report[package]['encodings'][encoding]['performances']
                )
            )

            y.add_row(
                [
                    package,
                    round(
                        (report[package]['encodings'][encoding]['success'] / (report[package]['encodings'][encoding]['success'] + report[package]['encodings'][encoding]['failure'])) * 100,
                        ndigits=2
                    ),
                    round(
                        mean(report[package]['encodings'][encoding]['similarities_in_failures']),
                        ndigits=3
                    ) if len(report[package]['encodings'][encoding]['similarities_in_failures']) > 0 else 'N/A',
                    mean_perf_ns,
                    round(
                        1. / (mean_perf_ns / 1e+9),
                        ndigits=3
                    ),
                    ', '.join(report[package]['encodings'][encoding]['confuse_it_with'])
                ]
            )

        print(
            y
        )
