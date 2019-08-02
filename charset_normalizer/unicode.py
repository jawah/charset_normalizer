from charset_normalizer.constant import UNICODE_RANGES_ZIP


class UnicodeRangeIdentify:

    SEARCH_TYPE_CACHE = dict()

    @staticmethod
    def find_letter_type(letter: str):
        """
        This method is intended to associate a single character with a range name from the unicode table
        :param str letter: Shall be a unique char
        :return: Associated unicode range designation
        :rtype: Union[str, None]
        """
        if len(letter) != 1:
            raise IOError('Trying to associate multiple char <{}> to a single unicode range'.format(letter))

        if ord(letter) in UnicodeRangeIdentify.SEARCH_TYPE_CACHE.keys():
            return UnicodeRangeIdentify.SEARCH_TYPE_CACHE[ord(letter)]

        for u_name, u_range in UNICODE_RANGES_ZIP.items():

            if ord(letter) in u_range:
                UnicodeRangeIdentify.SEARCH_TYPE_CACHE[ord(letter)] = u_name
                return u_name

        return None

    @staticmethod
    def is_accentuated(letter: str):
        """
        Verify if a latin letter is accentuated, unicode point of view.
        :param letter: Letter to check
        :return: True if accentuated, else False
        :rtype: bool
        """
        if len(letter) != 1:
            raise IOError('Trying to determine accentuated state of multiple char <{}>'.format(letter))
        return 192 <= ord(letter) <= 383
