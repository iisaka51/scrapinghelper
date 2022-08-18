import sys
import pytest

sys.path.insert(0,"../scrapinghelper")

from scrapinghelper.utils import (
    StrCase, is_alpha, is_alnum, omit_values, replace_values,
    add_df, df_compare, change_dict_keys, uDict, iDict
)
from pprint import pprint
from pathlib import Path
import numpy as np
import pandas as pd

class TestClass:
    def test_show_supported_case(self):
        expect = {'case': 'sample',
                 'snake': 'convert_case',
                 'kebab': 'convert-case',
                 'camel': 'convertCase',
                 'pascal': 'ConvertCase',
                 'const': 'CONVERT_CASE',
                 'sentence': 'Convert case',
                 'title': 'Convert Case',
                 'lower': 'convert case',
                 'upper': 'CONVERT CASE'}
        s = StrCase()
        result = s.show_supported_case()
        assert result == expect

    def test_conver_case_str(self):
        data = 'convert case'
        expect = { 'snake': 'convert_case',
                 'kebab': 'convert-case',
                 'camel': 'convertCase',
                 'pascal': 'ConvertCase',
                 'const': 'CONVERT_CASE',
                 'sentence': 'Convert case',
                 'title': 'Convert Case',
                 'lower': 'convert case',
                 'upper': 'CONVERT CASE'}
        s = StrCase()
        result = s.convert_case(data)
        assert result == expect['snake']
        for case in expect.keys():
            result = s.convert_case(data, case)
            assert result == expect[case]

    def test_conver_case_list(self):
        data = ['convert case', 'Convert Case']
        expect = { 'snake': ['convert_case','convert_case'],
                   'kebab': ['convert-case','convert-case'],
                   'camel': ['convertCase','convertCase'],
                   'pascal': ['ConvertCase','ConvertCase'],
                   'const': ['CONVERT_CASE','CONVERT_CASE'],
                   'sentence': ['Convert case','Convert case'],
                   'title': ['Convert Case','Convert Case'],
                   'lower': ['convert case','convert case'],
                   'upper': ['CONVERT CASE', 'CONVERT CASE']}
        s = StrCase()
        for case in expect.keys():
            result = s.convert_case(data, case)
            print(case)
            assert result == expect[case]

    def test_conver_case_nullval(self):
        data = ['', None, np.nan, pd.NA]
        expect = { 'snake': ['', None, np.nan, pd.NA],
                   'kebab': ['', None, np.nan, pd.NA],
                   'camel': ['', None, np.nan, pd.NA],
                   'pascal': ['', None, np.nan, pd.NA],
                   'const': ['', None, np.nan, pd.NA],
                   'sentence': ['', None, np.nan, pd.NA],
                   'title': ['', None, np.nan, pd.NA],
                   'lower': ['', None, np.nan, pd.NA],
                   'upper': ['', None, np.nan, pd.NA]}
        s = StrCase()
        for case in expect.keys():
            result = s.convert_case(data, case)
            assert result == expect[case]

    def test_conver_case_object(self):
        data = [10, 10.0, ['convert case'],
                ('convert case'), {'test': "convert case" } ]
        expect = { 'snake': [10, 10.0,
             ['convert_case'], ('convert_case'), {'test': "convert case" }],
                 'kebab': [10, 10.0,
             ['convert-case'], ('convert-case'), {'test': "convert case" }],
                 'camel': [10, 10.0,
             ['convertCase'], ('convertCase'), {'test': "convert case" }],
                 'pascal': [10, 10.0,
             ['ConvertCase'], ('ConvertCase'), {'test': "convert case" }],
                 'const': [10, 10.0,
             ['CONVERT_CASE'], ('CONVERT_CASE'), {'test': "convert case" }],
                 'sentence': [10, 10.0,
             ['Convert case'], ('Convert case'), {'test': "convert case" }],
                 'title': [10, 10.0,
             ['Convert Case'], ('Convert Case'), {'test': "convert case" }],
                 'lower': [10, 10.0,
             ['convert case'], ('convert case'), {'test': "convert case" }],
                 'upper': [10, 10.0,
             ['CONVERT CASE'], ('CONVERT CASE'), {'test': "convert case" }] }
        s = StrCase()

        for case in expect.keys():
            result = s.convert_case(data, case)
            assert result == expect[case]

    def test_is_alpha_alphabet(self):
        assert ( is_alpha('iisaka')
                 == True )

    def test_is_alpha_alphabet_with_number(self):
        assert ( is_alpha('iisaka51')
                 == False )

    def test_is_alpha_alphabet_with_symbol(self):
        assert ( is_alpha('@iisaka51')
                 == is_alpha('Goichi (iisaka) Yukawa')
                 == False )

    def test_is_alpha_kanji(self):
        assert ( is_alpha('京都市')
                 == False )

    def test_is_alpha_kanji_num(self):
        assert ( is_alpha('１２３')
                 == False )

    def test_is_alnum_alphabet(self):
        assert ( is_alnum('iisaka')
                 == True )

    def test_is_alnum_alphabet_with_number(self):
        assert ( is_alnum('iisaka51')
                 == True )

    def test_is_alnum_alphabet_with_symbol(self):
        assert ( is_alnum('@iisaka51')
                 == is_alnum('Goichi (iisaka) Yukawa')
                 == False )

    def test_is_alnum_kanji(self):
        assert ( is_alnum('京都市')
                 == False )

    def test_is_alnum_kanji_num(self):
        assert ( is_alpha('１２３')
                 == False )

    def test_df_compare(self):
        d1 = pd.DataFrame([ ['Kyoto', 35.0117,135.452],
                            ['Osaka', 34.4138,135.3808]],
                          columns=['cityName', 'latitude', 'longitude'])
        d2 = pd.DataFrame([ ['Kyoto', 35.0117,135.452],
                            ['Osaka', 34.4138,135.3808]],
                          columns=['cityName', 'latitude', 'longitude'])
        assert ( df_compare(d1, d2) == 0 )

    def test_df_compare_diff_count_non_zero(self):
        d1 = pd.DataFrame([ ['26100', 35.0117,135.452],
                            ['27100', 34.4138,135.3808]],
                          columns=['cityCode', 'latitude', 'longitude'])
        d2 = pd.DataFrame([ ['Kyoto', 35.0117,135.452],
                            ['Osaka', 34.4138,135.3808]],
                          columns=['cityName', 'latitude', 'longitude'])
        assert ( df_compare(d1, d2) != 0 )

    def test_omit_values(self):
        data = ['January', 'February', 'March', 'April',
                'May', 'June', 'July', 'August',
                'September', 'October', 'November', 'December']

        omits = ['April', 'September']

        expect = ['January', 'February', 'March', '',
                'May', 'June', 'July', 'August',
                '', 'October', 'November', 'December']
        result = omit_values(data, omits)
        assert result == expect

    def test_omit_values_ignore_case(self):
        data = ['January', 'February', 'March', 'April',
                'May', 'June', 'July', 'August',
                'September', 'October', 'November', 'December']

        omits = ['april', 'september']

        expect = ['January', 'February', 'March', '',
                'May', 'June', 'July', 'August',
                '', 'October', 'November', 'December']
        result = omit_values(data, omits, ignore_case=True)
        assert result == expect

    def test_omit_values_with_drop(self):
        data = ['January', 'February', 'March', 'April',
                'May', 'June', 'July', 'August',
                'September', 'October', 'November', 'December']

        omits = ['April', 'September']

        expect = ['January', 'February', 'March',
                'May', 'June', 'July', 'August',
                'October', 'November', 'December']
        result = omit_values(data, omits, drop=True)
        assert result == expect

    def test_omit_values_asstr(self):
        data = ( 'January' 'February' 'March' 'April'
                'May' 'June' 'July' 'August'
                'September' 'October' 'November' 'December' )

        omits = ['April', 'September']

        expect = ( 'January' 'February' 'March' ''
                'May' 'June' 'July' 'August'
                '' 'October' 'November' 'December' )

        result = omit_values(data, omits)
        assert result == expect

    def test_replace_values_list(self):
        data = ['January', 'February', 'March', 'April',
                'May', 'June', 'July', 'August',
                'September', 'October', 'November', 'December']

        replace = {'April': 'april', 'September': 'september' }

        expect = ['January', 'February', 'March', 'april',
                'May', 'June', 'July', 'August',
                'september', 'October', 'November', 'December']
        result = replace_values( data, replace)
        assert result == expect

    def convert_func(self, matchobj):
        map = {'January': '1',
               'February': '2' }
        return map[matchobj.group(0)]

    def test_replace_values_with_regexp(self):
        data = ['January', 'February', 'March', 'April',
                'May', 'June', 'July', 'August',
                'September', 'October', 'November', 'December']

        replace = { '.*ary': self.convert_func, '.*ber': 'BER' }

        expect = ['1', '2', 'March', 'April',
                'May', 'June', 'July', 'August',
                'BER', 'BER', 'BER', 'BER']
        result = replace_values( data, replace)
        assert result == expect

    def test_replace_values_ignore_case(self):
        data = ['January', 'February', 'March', 'April',
                'May', 'June', 'July', 'August',
                'September', 'October', 'November', 'December']

        replace = {'april': '4', 'september': '9' }

        expect = ['January', 'February', 'March', '4',
                'May', 'June', 'July', 'August',
                '9', 'October', 'November', 'December']
        result = replace_values( data, replace, ignore_case=True)
        assert result == expect

    def test_replace_values_list_inplace(self):
        data = ['January', 'February', 'March', 'April',
                'May', 'June', 'July', 'August',
                'September', 'October', 'November', 'December']

        replace = {'April': 'april', 'September': 'september' }

        expect = ['January', 'February', 'March', 'april',
                  'May', 'June', 'July', 'August',
                  'september', 'October', 'November', 'December']
        replace_values( data, replace, inplace=True)
        assert data == expect

    def test_replace_values_dict_val_default(self):
        data = { 1: 'January', 2: 'February', 3: 'March', 4: 'April',
                 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'September', 10: 'October', 11: 'November', 12: 'December'}

        replace = {'April': 'april', 'September': 'september' }

        expect = { 1: 'January', 2: 'February', 3: 'March', 4: 'april',
                 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'september', 10: 'October', 11: 'November', 12: 'December'}

        result = replace_values( data, replace )
        assert result == expect

    def test_replace_values_dict_val_explicit(self):
        data = { 1: 'January', 2: 'February', 3: 'March', 4: 'April',
                 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'September', 10: 'October', 11: 'November', 12: 'December'}

        replace = {'April': 'april', 'September': 'september' }

        expect = { 1: 'January', 2: 'February', 3: 'March', 4: 'april',
                 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'september', 10: 'October', 11: 'November', 12: 'December'}

        result = replace_values( data, replace, replace_for='value' )
        assert result == expect

    def test_replace_values_dict_val_ignore_case(self):
        data = { 1: 'January', 2: 'February', 3: 'March', 4: 'April',
                 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'September', 10: 'October', 11: 'November', 12: 'December'}

        replace = {'APRIL': 'april', 'SEPTEMBER': 'september' }

        expect = { 1: 'January', 2: 'February', 3: 'March', 4: 'april',
                 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'september', 10: 'October', 11: 'November', 12: 'December'}

        result = replace_values( data, replace, ignore_case=True )
        assert result == expect

    def test_replace_values_dict_inplace(self):
        data = { 1: 'January', 2: 'February', 3: 'March', 4: 'April',
                 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

        replace = {'April': 'april', 'September': 'september' }

        expect = { 1: 'January', 2: 'February', 3: 'March', 4: 'april',
                 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                 9: 'september', 10: 'October', 11: 'November', 12: 'December'}

        replace_values( data, replace, inplace=True )
        assert data == expect

    def test_replace_values_dict_keys(self):
        data = { 1: 'one', 2: 'two', 3: 'three', 4: 'four' }

        replace = {1: 'one',  2: 'two', 3: 'three'}

        expect = { 'one': 'one', 'two': 'two', 'three': 'three', 4: 'four' }

        result = replace_values( data, replace, replace_for='key')
        assert result == expect

    def test_replace_values_dict_val_obj(self):
        data = { 1: 'one', 2: 'two', 3: 'three', 4: 'four' }

        replace = {'one': 1, 'two': [2, 'two'], 'three': { 3: 'three'}}

        expect = { 1: 1, 2: [2, 'two'] , 3: {3: 'three'}, 4: 'four' }

        result = replace_values( data, replace )
        assert result == expect


    def test_change_dict_keys_case01(self):
        data = { 'January': 1, 'February': 2, 'March': 3, 'April': 4,
                 'May': 5, 'June': 6, 'July': 7, 'August': 8,
                 'September': 9, 'October': 10, 'November': 11, 'December': 12}
        replace = {'April': 4, 'September': 9 }
        expect = { 'January': 1, 'February': 2, 'March': 3, 4: 4,
                   'May': 5, 'June': 6, 'July': 7, 'August': 8,
                 9: 9, 'October': 10, 'November': 11, 'December': 12}
        result = change_dict_keys(data, replace)
        assert result == expect

    def test_change_dict_keys_case02(self):
        data = { 'January': 1, 'February': 2, 'March': 3, 'April': 4,
                 'May': 5, 'June': 6, 'July': 7, 'August': 8,
                 'September': 9, 'October': 10, 'November': 11, 'December': 12}
        replace = {'April': 4, 'September': 9 }
        expect = { 'January': 1, 'February': 2, 'March': 3, 4: 4,
                   'May': 5, 'June': 6, 'July': 7, 'August': 8,
                 9: 9, 'October': 10, 'November': 11, 'December': 12}
        change_dict_keys(data, replace, inplace=True)
        assert data == expect

    def test_change_dict_keys_case03(self):
        data = { 1: 'January', 2: 'February', 3: 'March', 4: 'April',
                 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
        replace = {4: 'Apr', 7: 'Jul' }
        expect = { 1: 'January', 2: 'February', 3: 'March', 'Apr': 'April',
                 5: 'May', 6: 'June', 'Jul': 'July', 8: 'August',
                 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
        result = change_dict_keys(data, replace)
        assert result == expect

    def test_change_dict_keys_case04(self):
        data = { 'January': 1, 'February': 2, 'March': 3, 'April': 4,
                 'May': 5, 'June': 6, 'July': 7, 'August': 8,
                 'September': 9, 'October': 10, 'November': 11, 'December': 12}
        expect = { 'January': 1, 'February': 2, 'March': 3, 'Apr': 4,
                   'May': 5, 'June': 6, 'July': 7, 'August': 8,
                 'September': 9, 'October': 10, 'November': 11, 'December': 12}
        result = change_dict_keys(data, 'April', 'Apr')
        assert result == expect

    def test_change_dict_keys_case05(self):
        data = { 'January': 1, 'February': 2, 'March': 3, 'April': 4,
                 'May': 5, 'June': 6, 'July': 7, 'August': 8,
                 'September': 9, 'October': 10, 'November': 11, 'December': 12}
        expect = { 'January': 1, 'February': 2, 'March': 3, 'Apr': 4,
                   'May': 5, 'June': 6, 'July': 7, 'August': 8,
                 'September': 9, 'October': 10, 'November': 11, 'December': 12}
        change_dict_keys(data, 'April', 'Apr', inplace=True)
        assert data == expect

    def test_udict_case01(self):
        data = { 'January': 1, 'February': 2, 'March': 3, 'April': 4 }
        expect = { 'January': 1, 'February': 2, 'March': 3, 'April': 4 }
        result = uDict(data)
        assert result == data

    def test_udict_case02(self):
        expect = { 'January': 1, 'February': 2, 'March': 3, 'April': 4 }
        result = uDict(January=1, February=2, March=3, April=4)
        assert result == expect

    def test_udict_case03(self):
        data = uDict({ 'January': 1, 'February': 2, 'March': 3, 'April': 4 })
        expect = { 'January': 1, 'February': 2, 'March': 3, 'April': 4 }
        assert data == expect

    def test_udict_case04(self):
        data = uDict({ 'January': 1, 'February': 2, 'March': 3, 'April': 4 })
        expect = { 'January': 1, 'February': 2, 'March': 3, 'Apr': 4 }
        saved = data.copy()
        result = data.replace_key('April', 'Apr')
        assert ( result == expect
                 and data == saved )

    def test_udict_case05(self):
        data = uDict({ 'January': 1, 'February': 2, 'March': 3, 'April': 4 })
        replace = {'January': 'Jan', 'February': 'Feb' }
        expect = { 'Jan': 1, 'Feb': 2, 'March': 3, 'April': 4 }
        saved = data.copy()
        result = data.replace_key_map(replace)
        assert ( result == expect
                 and data == saved )

    def test_udict_case06(self):
        data = uDict({ 'January': 1, 'February': 2, 'March': 3, 'April': 4 })
        replace = {'January': 'Jan', 'February': 'Feb' }
        expect = { 'Jan': 1, 'Feb': 2, 'March': 3, 'April': 4 }
        saved = data.copy()
        data.replace_key_map(replace, inplace=True)
        assert ( data == expect
                 and data != saved )

    def test_udict_case07(self):
        data = uDict({ 'January': 1, 'February': 2, 'March': 3, 'April': 4 })
        with pytest.raises(TypeError) as e:
            result = dict({data: 1})
        assert str(e.value) == "unhashable type: 'uDict'"

    def test_idict_case01(self):
        data = { 'January': 1, 'February': 2, 'March': 3, 'April': 4 }
        expect = { 'January': 1, 'February': 2, 'March': 3, 'April': 4 }
        result = iDict(data)
        assert result == data

    def test_idict_case02(self):
        expect = { 'January': 1, 'February': 2, 'March': 3, 'April': 4 }
        result = iDict(January=1, February=2, March=3, April=4)
        assert result == expect

    def test_idict_case03(self):
        data = iDict({ 'January': 1, 'February': 2, 'March': 3, 'April': 4 })
        expect = { 'January': 1, 'February': 2, 'March': 3, 'April': 4 }
        assert data == expect

    def test_idict_case04(self):
        data = iDict({ 'January': 1, 'February': 2, 'March': 3, 'April': 4 })
        with pytest.raises(TypeError) as e:
            data['January'] = 'Jan'
        assert str(e.value) == 'iDict object does not support item assignment'

    def test_idict_case05(self):
        data = iDict({ 'January': 1, 'February': 2, 'March': 3, 'April': 4 })
        with pytest.raises(AttributeError) as e:
            result  = data.pop()
        assert str(e.value) == 'iDict object has no attribute pop'

    def test_idict_case06(self):
        data = iDict({ 'January': 1, 'February': 2, 'March': 3, 'April': 4 })
        with pytest.raises(AttributeError) as e:
            data.clear()
        assert str(e.value) == 'iDict object has no attribute clear'

    def test_idict_case07(self):
        data = iDict({ 'January': 1, 'February': 2, 'March': 3, 'April': 4 })
        with pytest.raises(AttributeError) as e:
            data.update({ 'January': 1, 'February': 2, 'March': 3, 'April': 4 })
        assert str(e.value) == 'iDict object has no attribute update'

    def test_idict_case08(self):
        data = iDict({ 'January': 1, 'February': 2, 'March': 3, 'April': 4 })
        with pytest.raises(AttributeError) as e:
            data.setdefault('May', 5)
        assert str(e.value) == 'iDict object has no attribute setdefault'

    def test_idict_case09(self):
        data = iDict({ 'January': 1, 'February': 2, 'March': 3, 'April': 4 })
        assert hasattr(data, '__hash__') == True

    def test_idict_case09(self):
        data = iDict({ 'January': 1, 'February': 2, 'March': 3, 'April': 4 })
        result = dict({data: 1})
        assert  result[data]  == 1
