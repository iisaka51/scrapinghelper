import re
from typing import Any, Dict, Union
import numpy as np
import pandas as pd
from functools import singledispatch
from .singledispatchmethod import singledispatchmethod
from unicodedata import normalize

__all__ = {
    "StrVal",
    "is_alpha",
    "is_alnum",
    "omit_values",
    "replace_values",
    "add_df",
    "df_compare"
}

def is_alpha(word: str)-> bool:
    """ Check word is alphabet.
    Parameters
    ----------
    word: str
        any string

    Returns
    -------
    validate result: bool
        if all characters of word, return ``True`` otherwise return ``False``
    """
    try:
        return word.encode('ascii').isalpha()
    except:
        return False

def is_alnum(word: str)-> bool:
    """ Check word is alphabet and digits.
    Parameters
    ----------
    word: str
        any string

    Returns
    -------
    validate result: bool
        if all characters of word, return ``True`` otherwise return ``False``
    """
    try:
        return word.encode('ascii').isalnum()
    except:
        return False

# singledispatch can regist for only first arguments.

@singledispatch
def replace_values( *arg: Any, **kwargs: Any) ->Any:
    """dispatch function replace_values """
    raise TypeError('Unsupport Type')

@replace_values.register
def _replace_values_multi(
        replace: dict,
        values: list,
        ignore_case: bool=False,
    )-> list:
        flags = [ re.UNICODE, ( re.IGNORECASE + re.UNICODE) ]

        for n in range(len(values)):
            for old, new in replace.items():
                values[n] = re.sub(old, new,  values[n],
                                   flags = flags[ignore_case])
        return values

@replace_values.register
def _replace_values_single(
        replace_from: list,
        replace_to: str,
        values: Union[list, str],
        ignore_case: bool=False,
    )-> list:

        if isinstance(values, str):
            as_str = True
            values = [values]
        else:
            as_str = False

        flags = [ re.UNICODE, ( re.IGNORECASE + re.UNICODE) ]
        for n in range(len(values)):
            for old in replace_from:
                values[n] = re.sub( old, replace_to, values[n],
                                   flags = flags[ignore_case])
        if as_str:
            return values[0]
        else:
            return values

@singledispatch
def omit_values( *arg: Any, **kwargs) ->Any:
    """dispatch function omit_values """
    raise TypeError('Unsupport Type')

@omit_values.register
def _omit_values_muti(
        values: list,
        omits: list,
        ignore_case: bool=False,
        drop: bool=False
    )-> list:
        values =  _replace_values_single(omits, '', values,
                      ignore_case=ignore_case)
        if drop:
            count = values.count('')
            for _ in range(count):
                values.remove('')
        return values

@omit_values.register
def _omit_values_str(
        values: str,
        omits: list,
        ignore_case: bool=False,
    )-> list:
        return _replace_values_single(omits, '', values)


def add_df(
        values: list,
        columns: list,
        omits: list=[]
    ) ->pd.DataFrame:

        if omits:
            values = self.omit_chars(values,omits)
            columns = self.omit_chars(columns,omits)

        # Since Pandas 1.3.0
        df = pd.DataFrame(values,index=columns)._maybe_depup_names(columns)
        self.df = pd.concat([self.df,df.T])

def df_compare(
        df1: pd.DataFrame,
        df2: pd.DataFrame,
    ) -> int:
    """ Compare DataFrame
    Parameters
    ----------
    df1: pd.DataFrame, df2: pd.DataFrame
        any DataFrame to compare

    Returns
    -------
    validate result: Union[bool,int]
    """

    diff_df = pd.concat([df1,df2]).drop_duplicates(keep=False)
    diffs = len(diff_df)
    return diffs


class StrCase(object):

    def __init__(self):
        self.__NULL_VALUES = {"", None, np.nan, pd.NA}

        self.__supported_case = {
            "snake": {
                'sample': 'convert_case',
                'separaator': '_',
                'splitor': self.split_strip_string,
                'convertor': lambda x: "_".join(x).lower() },
            "kebab": {
                'sample': 'convert-case',
                'separaator': '-',
                'splitor': self.split_strip_string,
                'convertor': lambda x: "-".join(x).lower() },
            "camel": {
                'sample': 'convertCase',
                'separaator': '',
                'splitor': self.split_strip_string,
                'convertor': lambda x: x[0].lower() + "".join(w.capitalize() for w in x[1:]) },
            "pascal": {
                'sample': 'ConvertCase',
                'separaator': '',
                'splitor': self.split_strip_string,
                'convertor': lambda x:  "".join(w.capitalize() for w in x) },
            "const": {
                'sample': 'CONVERT_CASE',
                'separaator': '_',
                'splitor': self.split_strip_string,
                'convertor':  lambda x: "_".join(x).upper() },
            "sentence": {
                'sample': 'Convert case',
                'splitor': self.split_string,
                'convertor':  lambda x: " ".join(x).capitalize() },
            "title": {
                'sample': 'Convert Case',
                'separaator': ' ',
                'splitor': self.split_string,
                'convertor':  lambda x: " ".join(w.capitalize() for w in x) },
            "lower": {
                'sample': 'convert case',
                'separaator': ' ',
                'splitor': self.split_string,
                'convertor':  lambda x:  " ".join(x).lower() },
            "upper": {
                'sample': 'CONVERT CASE',
                'separaator': ' ',
                'splitor': self.split_string,
                 'convertor': lambda x: " ".join(x).upper() },
        }


    def show_supported_case(self, verbose=False):
        header = { "case":  "sample" }
        case_sample = dict(header,
           **{ case: "{}".format(self.__supported_case[case]['sample'])
                    for case in self.__supported_case.keys() } )
        if verbose:
            print(case_sample)
        return case_sample

    @classmethod
    def split_strip_string(cls, string: str) -> list:
        """Split the string into separate words and strip punctuation."""
        string = re.sub(r"[!()*+\,\-./:;<=>?[\]^_{|}~]", " ", string)
        string = re.sub(r"[\'\"\`]", "", string)

        return re.sub(
            r"([A-Z][a-z]+)",
            r" \1", re.sub(r"([A-Z]+|[0-9]+|\W+)",
            r" \1",
            string)
        ).split()

    @classmethod
    def split_string(cls, string: str) -> list:
        """Split the string into separate words."""
        string = re.sub(r"[\-_]", " ", string)

        return re.sub(
            r"([A-Z][a-z]+)",
            r" \1",
            re.sub(r"([A-Z]+)",
            r"\1", string)
        ).split()

    @singledispatchmethod
    def convert_case(self, *args: Any, **kwargs: Any) -> Any:
        """ dispatch function """
        raise TypeError('Unsupport Type')

    @convert_case.register(type(None))
    def _conver_case_none(self,
            obj: type(None),
            *args: Any,
            **kwargs: Any
        ):
        """ Catch NULL values and return it"""
        return obj

    @convert_case.register( type(np.nan))
    def _conver_case_npnan(self,
            obj: type(np.nan),
            *args: Any,
            **kwargs: Any
        ) -> np.nan:
        """ Catch NULL values and return it"""
        return obj

    @convert_case.register( type(pd.NA))
    def _conver_case_pdna(self,
            obj: type(pd.NA),
            *args: Any,
            **kwargs: Any
        ) -> pd.NA:
        """ Catch NULL values and return it"""
        return obj

    @convert_case.register(str)
    def _convert_case_str(self,
            obj: str,
            case: str='snake',
            na_values: str='',
            *args: Any,
            **kwargs: Any
        ) -> str:
        """Convert case style for obj.

        Parameters
        ----------
        obj: Any
            convert case for obj
        case: str
            Preferred case type, i.e.:  (default: 'snake')
            check `.show_supported_case()`

        na_values: str
            Additional strings to recognize as NA/NaN.
            default is '' for str, otherwise 'NaN'

            i.e.: '', '#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN',
                  '-NaN', '-nan', '1.#IND', '1.#QNAN', '<NA>', 'N/A',
                  'NA', 'NULL', 'NaN', 'n/a', 'nan', 'null'.

        Returns:
        --------
        converted string: str
        """

        if obj in self.__NULL_VALUES:
            na_values = na_values or "" if isinstance(obj, str) else "NaN"

        if case in self.__supported_case:
            words = self.__supported_case[ case ]['splitor'](obj)
            string = self.__supported_case[ case ]['convertor'](words)

        return string


    @convert_case.register(list)
    def _convert_case_list(self,
            obj: list,
            case: str='snake',
            na_values: str='',
            *args: Any,
            **kwargs: Any
        ) -> list:
        """Convert case style for list of obj."""

        return [ self.convert_case(x, case, na_values) for x in obj ]

    def replace_values(self, string: Any, mapping: Dict[str, str]) -> Any:
        """Replace string values in string.

        Parameters
        ----------
        string: Any
            string.
        mapping
            Maps old values in the string to the new string.
        """
        if string in NULL_VALUES:
            return string

        string = str(string)
        for old_value, new_value in mapping.items():
            # If the old value or the new value is not alphanumeric,
            # add underscores to the beginning and end
            # so the new value will be parsed correctly for self.convert_case()
            new_val = (
                r"{}".format(new_value)
                if is_alnum(old_value) and is_alnum(new_value)
                else r"_{}_".format(new_value)
            )
            string = re.sub(
                r"{}".format(old_value),
                new_val, string, flags=re.IGNORECASE)

        return string

    def remove_accents(self, string: Any) -> Any:
        """Return the normal form for a Unicode string
           using canonical decomposition."""

        if not isinstance(string, str):
            return string

        return ( normalize("NFD", string)
                 .encode("ascii", "ignore")
                 .decode("ascii") )

    def rename_duplicates(self, strings: list, case: str) -> Any:
        """Rename duplicated strings to append a number at the end."""
        counts: Dict[str, int] = {}

        if case in self.__supported_case:
            separaator = self.__supported_case[case]['separaator']

        for i, col in enumerate(strings):
            cur_count = counts.get(col, 0)
            if cur_count > 0:
                strings[i] = "{}{}{}".format(col, separaator, cur_count)
            counts[col] = cur_count + 1

        return strings
