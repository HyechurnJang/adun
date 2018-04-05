# -*- coding: utf-8 -*-
'''
Created on 2018. 4. 2.
@author: HyechurnJang
'''

import re


mac = 'AA:AA:AA:AA:AA:A3'
ip = '123.123.123.1'

print re.search('^\w\w:\w\w:\w\w:\w\w:\w\w:\w\w$', mac)
print re.search('^\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?$', ip)