import sys

sys.path.insert(0,"../scrapinghelper")

from scrapinghelper.utils import (
    StrCase, is_alpha, is_alnum, omit_values, replace_values,
    add_df, df_compare
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

    def test_replace_values_dict_val(self):
        data = { 1: 'January', 2: 'February', 3: 'March', 4: 'April',
                 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'September', 10: 'October', 11: 'November', 12: 'December'}

        replace = {'April': 'april', 'September': 'september' }

        expect = { 1: 'January', 2: 'February', 3: 'March', 4: 'april',
                 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'september', 10: 'October', 11: 'November', 12: 'December'}

        result = replace_values( data, replace )
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

    def test_replace_values_dict_val_ignore_case(self):
        data = { 1: 'January', 2: 'February', 3: 'March', 4: 'April',
                 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'September', 10: 'October', 11: 'November', 12: 'December'}

        replace = {'april': 'april', 'september': 'september' }

        expect = { 1: 'January', 2: 'February', 3: 'March', 4: 'april',
                 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'september', 10: 'October', 11: 'November', 12: 'December'}

        result = replace_values( data, replace, ignore_case=True )
        assert result == expect

    def test_replace_values_dict_key(self):
        data = { 'January': 'January', 'February': 'February',
                 'March': 'March', 'April': 'April', 'May': 'May',
                 'June': 'June', 'July': 'July', 'August': 'August',
                 'September': 'September', 'Octorber': 'October',
                 'November': 'November', 'December': 'December'}

        replace = {'April': 'april', 'September': 'september' }

        expect = { 'January': 'January', 'February': 'February',
                 'March': 'March', 'april': 'April', 'May': 'May',
                 'June': 'June', 'July': 'July', 'August': 'August',
                 'september': 'September', 'Octorber': 'October',
                 'November': 'November', 'December': 'December'}

        result = replace_values( data, replace,
                                   replace_key=True, replace_value=False )
        assert result == expect

    def test_replace_values_dict_key_val(self):
        data = { 'January': 'January', 'February': 'February',
                 'March': 'March', 'April': 'April', 'May': 'May',
                 'June': 'June', 'July': 'July', 'August': 'August',
                 'September': 'September', 'Octorber': 'October',
                 'November': 'November', 'December': 'December'}

        replace = {'April': 'april', 'September': 'september' }

        expect = { 'January': 'January', 'February': 'February',
                 'March': 'March', 'april': 'april', 'May': 'May',
                 'June': 'June', 'July': 'July', 'August': 'August',
                 'september': 'september', 'Octorber': 'October',
                 'November': 'November', 'December': 'December'}

        result = replace_values( data, replace,
                                   replace_key=True, replace_value=True )
        assert result == expect

