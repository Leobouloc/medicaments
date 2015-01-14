# -*- coding: utf-8 -*-
"""
Created on Wed Jan 07 20:45:03 2015

@author: alexis
"""

import os
import pandas as pd
import numpy as np
import pdb

import matplotlib.pyplot as plt

from load_data.bdm_from_scrap import bdm_scrap
from load_data.medic_gouv import load_medic_gouv
from load_data.bdm_cnamts.get_bdm import load_cip
from load_data.bdm_cnamts.bdm_scrap import parse_list
from CONFIG import path_PMF


dates = [100*year + month + 1
         for year in range(2009, 2014)
         for month in range(12)]

os.chdir(path_PMF)

with open('list_cip.txt', 'r') as f:
    cip = f.read().split(',')

#gouv = load_medic_gouv(var_to_keep = ['CIP', 'Titulaires',
##                                      'Label_presta',
#                                      'Statu_admin_presta', 'Nom',
#                                      'Id_Groupe', 'Nom_Groupe',
#                                      'Type'])
##scrap = bdm_scrap()
#print len(cip)
#
#var_en_gouv = [x for x in cip if x in gouv['CIP'].values]
#print len(var_en_gouv)
#
#var_not_gouv = [x for x in cip if x not in gouv['CIP'].values]
#print len(var_not_gouv)
#
#
#gouv = gouv[gouv['CIP'].isin(cip)]
#
#var_en_gouv = [x for x in gouv['CIP'] if x in cip]
#
#gouv.loc[gouv.Nom.str.contains('IBUP') == True]
#gouv.loc[gouv.Nom.str.contains('DOLIPRAN') == True]
#
#gouv.loc[gouv.Nom.str.contains('PARAC') == True]
#
#gouv.loc[gouv.Nom.str.contains('RHUM') == True]

bdm = bdm_scrap()
print len(cip)
var_en_bdm = [x for x in cip if x in bdm['CIP'].values]
print len(var_en_bdm)

var_not_bdm = [x for x in cip if x not in bdm['CIP'].values]
var_not_bdm_html = [x + '.html' for x in var_not_bdm]
print len(var_not_bdm)

#for cip in var_not_bdm:
#    load_cip(cip, 'cip')
table, warn, prob = parse_list(var_not_bdm_html)