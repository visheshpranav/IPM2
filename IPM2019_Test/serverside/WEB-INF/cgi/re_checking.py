# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 14:09:00 2020

@author: v.a.subhash.krishna
"""

import re

def numeric_check(value):
    re_check = re.fullmatch(r'[0-9]+',value)
    if re_check:
        return True
    return False

def alphanumeric_hypen_check(value):
    re_check = re.fullmatch(r'^[0-9a-zA-Z_]+$',value)
    if re_check:
        return True
    return False

if __name__ == '__main__':
    print(numeric_check('123'))
