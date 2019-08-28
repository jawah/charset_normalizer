from chardet import detect
from cchardet import detect as n_detect
from charset_normalizer import CharsetNormalizerMatches
from statistics import mean
import locale
from tqdm import tqdm

from time import perf_counter_ns
from glob import glob
import prettytable

locale.setlocale(locale.LC_ALL, 'fr-FR')

N_REQUIRED_LOOP = 50

if __name__ == '__main__':

    st_ar = dict()
    st_re = dict()

    for srt_file in tqdm(glob('./data/*.srt') + glob('./data/*.txt')):

        st_ar[srt_file] = dict()
        st_re[srt_file] = dict()

        with open(srt_file, 'rb') as fp:
            seq_ = fp.read()

            l_ = list()

            for i in range(N_REQUIRED_LOOP):
                st_t = perf_counter_ns()
                k_ = detect(seq_)
                l_.append(perf_counter_ns() - st_t)

            st_ar[srt_file]['chardet'] = locale.format_string('%d', mean(l_), grouping=True)
            st_re[srt_file]['chardet'] = k_['encoding']

            l_.clear()

            for i in range(N_REQUIRED_LOOP):
                st_t = perf_counter_ns()
                z_ = n_detect(seq_)
                l_.append(perf_counter_ns() - st_t)

            st_ar[srt_file]['cchardet'] = locale.format_string('%d', mean(l_), grouping=True)
            st_re[srt_file]['cchardet'] = z_['encoding']

            l_.clear()

            for i in range(N_REQUIRED_LOOP):
                st_t = perf_counter_ns()
                y_ = CharsetNormalizerMatches.from_bytes(seq_)
                l_.append(perf_counter_ns() - st_t)

            st_ar[srt_file]['charset_normalizer'] = locale.format_string('%d', mean(l_), grouping=True)
            st_re[srt_file]['charset_normalizer'] = y_.best().first().encoding

    x_ = prettytable.PrettyTable(['File', 'Chardet', 'cChardet', 'Charset Normalizer'])

    for k, v in st_ar.items():
        x_.add_row(
            [
                k,
                v['chardet'],
                v['cchardet'],
                v['charset_normalizer']
            ]
        )

    print(x_)

    x_ = prettytable.PrettyTable(['File', 'Chardet', 'cChardet', 'Charset Normalizer'])

    for k, v in st_re.items():
        x_.add_row(
            [
                k,
                v['chardet'],
                v['cchardet'],
                v['charset_normalizer']
            ]
        )

    print(x_)
