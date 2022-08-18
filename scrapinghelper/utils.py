import re
from typing import Any, Dict, Union, Optional, Hashable, Literal, get_args
import numpy as np
import pandas as pd
from multimethod import multidispatch, multimethod
from unicodedata import normalize
from collections import OrderedDict
from enum import Enum

__all__ = [
    "uDict",
    "iDict",
    "StrCase",
    "is_alpha",
    "is_alnum",
    "ordereddict_to_dict",
    "change_dict_keys",
    "omit_values",
    "replace_values",
    "add_df",
    "df_compare",
    "ReplaceFor",
    "ReplaceForType",
]

class ReplaceFor(str, Enum):
  KEY = "key"
  VALUE = "value"

ReplaceForType = Literal[ReplaceFor.KEY, ReplaceFor.VALUE]

class uDict(dict):
    def __missing__(self, key):
        return None

    def __hash__(self):
        return hash(tuple(sorted(self.items())))

    def replace_key(self, old, new):
        self.replace_key_map({old: new})

    def replace_key_map(self, replace):
        new_dict = {}
        for key in list(self.keys()):
            new_dict[replace.get(key, key)] = self[key]
        self.update(new_dict)

    def fromkeys(self, S, v):
        return type(self)(dict(self).fromkeys(S, v))

class iDict(dict):
    def __missing__(self, key):
        return None

    def __setitem__(self, key, value):
        raise TypeError(
            r"{} object does not support item assignment"
            .format(type(self).__name__) )

    def __delitem__(self, key):
        raise TypeError(
            r"{} object does not support item deletion"
            .format(type(self).__name__) )

    def __getattribute__(self, attribute):
        if attribute in ('clear', 'update', 'pop', 'popitem', 'setdefault'):
            raise AttributeError(
                r"{} object has no attribute {}"
                .format(type(self).__name__, attribute) )
        return dict.__getattribute__(self, attribute)

    def __hash__(self):
        return hash(tuple(sorted(self.items())))

    def fromkeys(self, S, v):
        return type(self)(dict(self).fromkeys(S, v))

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
    :param word: str
        any string

    "returns:  validate result
        if all characters of word, return ``True`` otherwise return ``False``
    """
    try:
        return word.encode('ascii').isalnum()
    except:
        return False

@multidispatch
def ordereddict_to_dict( obj: Any) -> dict:
    raise TypeError("Unsupported type.")

@ordereddict_to_dict.register(str)
def _ordereddict_to_dict(obj: str):
    return obj

@ordereddict_to_dict.register(Union[int, float])
def _ordereddict_to_dict(obj: Union[int, float]) ->Union[int, float]:
    return obj

@ordereddict_to_dict.register(dict)
def _ordereddict_to_dict(obj: dict) ->dict:
    return {k: ordereddict_to_dict(v) for k, v in obj.items()}

@ordereddict_to_dict.register(OrderedDict)
def _ordereddict_to_dict(obj: OrderedDict) ->dict:
    return dict(obj)

@ordereddict_to_dict.register(Union[list, tuple])
def _ordereddict_to_dict(obj: Union[list, tuple]) ->list:
    return [ordereddict_to_dict(e) for e in obj]

@multidispatch
def change_dict_keys( *args: Any, **kwargs: Any):
    raise TypeError("Invaid Type.")

@change_dict_keys.register(dict, Hashable, Hashable)
def _change_dict_keys_single(
    data: dict,
    old: Hashable,
    new: Hashable,
    inplace: bool=False,
    ) -> dict:
    """Change dict key.
    Parameters
    ----------
    data: dict
         old dict
    old: Hashable
         old key
    new: Hashable
         new key
    inplace: bool
        Whether to perform the operation in place on the data. default False.
    Returns
    -------
    new dict: dict
    """

    if not inplace:
        data = data.copy()

    workdict = {}
    replace={old:new}
    for key in list(data.keys()):
        data[replace.get(key,key)] = data.pop(key)

    if not inplace:
        return data

@change_dict_keys.register(dict, dict)
def _change_dict_keys_multi(
        data: dict,
        replace: dict,
        inplace: bool=False,
    ) -> dict:
    """Change dict key using dict.
    Parameters
    ----------
    d: dict
         old dict
    replace: dict {old_key: new_key,...}
        replace keymap as dict.
    inplace: bool
        Whether to perform the operation in place on the data. default False.
    Returns
    -------
    new dict: dict
    """

    if not inplace:
        data = data.copy()

    for key in list(data.keys()):
        data[replace.get(key, key)] = data.pop(key)

    if not inplace:
        return data


@multidispatch
def replace_values( obj: Any, *arg: Any, **kwargs: Any) ->Any:
    """dispatch function replace_values """
    if obj:
        return obj

@replace_values.register(list, dict)
def _replace_values_multi(
        values: list,
        replace: dict,
        *,
        ignore_case: bool=False,
        inplace: bool=False,
        **kwargs: Any,
    )-> Optional[list]:

        if not inplace:
            values = values.copy()

        flags = [ re.UNICODE, ( re.IGNORECASE + re.UNICODE) ]
        for n in range(len(values)):
            for old, new in replace.items():
                values[n] = re.sub(old, new,  values[n],
                                   flags = flags[ignore_case])
        if not inplace:
            return values

@replace_values.register(dict, dict)
def _replace_values_dict_multi(
        values: dict,
        replace: dict,
        *,
        ignore_case: bool=False,
        inplace: bool=False,
        replace_for: ReplaceForType = ReplaceFor.VALUE
    )-> Optional[list]:
        """replace values of dict
        Parameters
        ----------
        values: dict
           to replace data
        replace: dict
           replace map. { old: new,....}
        replace_for: avaiable 'key', 'value'.
           If replace_for set 'value', replace 'value' of dict.
           If replace_value set 'key', replace 'key' of dict.
           default is 'value'
        """
        if replace_for not in get_args(ReplaceForType):
            raise ValueError("replace_for must be 'key' or 'value'.")

        if replace_for == ReplaceFor.KEY:
            mapper={}
            for key, value in list(values.items()):
                for old, new in replace.items():
                    new_key = replace_values(key, [old], new,
                                             ignore_case=ignore_case)
                    if new == new_key:
                        mapper[key] = new_key

            workdict = values.copy()
            for key, value in list(workdict.items()):
                workdict[mapper.get(key, key)] = workdict.pop(key)

        if replace_for == ReplaceFor.VALUE:
            workdict = values.copy()
            mapper={}
            for key, value in list(workdict.items()):
                for old, new in replace.items():
                    if isinstance(value, str) and ignore_case:
                        new_val = replace_values(value, [old], new,
                                         ignore_case=ignore_case)
                        if new == new_val:
                            mapper[value] = new_val
                    else:
                        if value == old:
                            mapper[value] = new

            for key, value in list(workdict.items()):
                workdict[key] = mapper.get(value, workdict.pop(key))

        if inplace:
            values.update(workdict)
        else:
            return workdict

@replace_values.register(list, list, str)
def _replace_values_single_str(
        values: list,
        replace_from: list,
        replace_to: str,
        *,
        ignore_case: bool=False,
        inplace: bool=False,
        **kwargs: Any,
    )-> Optional[list]:

        if not inplace:
            values = values.copy()

        flags = [ re.UNICODE, ( re.IGNORECASE + re.UNICODE) ]
        for n in range(len(values)):
            for old in replace_from:
                values[n] = re.sub( old, replace_to, values[n],
                                   flags = flags[ignore_case])
        if not inplace:
            return values

@replace_values.register(list, list, Any)
def _replace_values_single_obj(
        values: list,
        replace_from: list,
        replace_to: Any,
        *,
        ignore_case: bool=False,
        inplace: bool=False,
        **kwargs: Any,
    )-> Optional[list]:

        if not inplace:
            values = values.copy()

        for n in range(len(values)):
            for old in replace_from:
                if values[n] ==  old:
                    values[n] = new

        if not inplace:
            return values


@replace_values.register(str, list, Hashable)
def _replace_values_text(
        values: str,
        replace_from: list,
        replace_to: Hashable,
        *,
        ignore_case: bool=False,
        **kwargs: Any,
    )-> Hashable:

        flags = [ re.UNICODE, ( re.IGNORECASE + re.UNICODE) ]
        for old in replace_from:
            if isinstance(old, str) and isinstance(replace_to, str):
                values = re.sub( old, replace_to, values,
                             flags = flags[ignore_case])
            elif old == origin:
                values = replace_to

        return values


@replace_values.register(Union[int, float], list, Any)
def _replace_values_number(
        values: Union[int, float],
        replace_from: list,
        replace_to: Any,
        **kwargs: Any,
    )-> str:
        if values in replace_from:
            return replace_to
        else:
            return values


@multidispatch
def omit_values( obj: Any, *arg: Any, **kwargs: Any) ->Any:
    """dispatch function replace_values """
    if obj:
        return obj

@omit_values.register(list, list)
def _omit_values_multi(
        values: list,
        omits: list,
        *,
        inplace: bool=False,
        ignore_case: bool=False,
        drop: bool=False
    )-> list:
        if not inplace:
            values = values.copy()

        values =  replace_values(values, omits, '', ignore_case=ignore_case)
        if drop:
            count = values.count('')
            for _ in range(count):
                values.remove('')

        if not inplace:
            return values

@omit_values.register(str, list)
def omit_values_single(
        values: str,
        omits: list,
        *,
        ignore_case: bool=False,
    )-> str:
        return replace_values(values, omits, '', ignore_case=ignore_case)


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

    @multimethod
    def convert_case(self, obj: Any, *args: Any, **kwargs: Any) -> Any:
        """ dispatch function """
        return obj

    @convert_case.register
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
            return na_values

        if case in self.__supported_case:
            words = self.__supported_case[ case ]['splitor'](obj)
            string = self.__supported_case[ case ]['convertor'](words)

        return string


    @convert_case.register
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
        if string in self.__NULL_VALUES:
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
