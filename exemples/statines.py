# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 22:37:37 2014

@author: alexis
"""
import matplotlib.pyplot as plt

from exploitation_sniiram import get_base_brute
from display_and_graphs import graph_volume_classe
from outils import all_periods

base_brute = get_base_brute()

base_brute

statine = base_brute[base_brute['CODE_ATC_4'] == "C10AA"]
statine['Id_Groupe'].value_counts(dropna=False)
statine['premiere_vente'].value_counts(dropna=False)
statine['premiere_vente'].hist(bins=50)
statine['premiere_vente'].hist(by=statine['Id_Groupe'], bins=50)

test = statine.groupby('Id_Groupe').sum()
test[all_periods(statine)[3]].T.plot()


test = statine.groupby(['CODE_ATC','Type']).sum()
test[all_periods(statine)[3]].T.plot()

princeps = statine[statine['Type']==0]
princeps.groupby('CODE_ATC').sum()[all_periods(statine)[3]].T.plot()


statine
statine.iloc[:,:10]
sel = gouv.CIP.isnull()
statine['Code_Substance']
statine['Code_Substance'].value_counts()
statine['Id_Group'].value_counts()
statine['Id_Groupe'].value_counts()
statine = base_brute[base_brute['CODE_ATC'] == "C10AA05"]
statine
statine = base_brute[base_brute['CODE_ATC'] == "C10AA05"]
statine
statine['CIP']

graph_volume_classe(base_brute, input_val="C10AA05", display='volume', make_sum=False)
graph_volume_classe(base_brute, input_val="C10AA05", make_sum=True)

statine = base_brute[base_brute['CODE_ATC_4'] == "C10AA"]

#import display_and_graphs as dis
#dis.graph_prix_classe('C10AA')
#graph_volume_classe(CODE_ATC="C10AA05")
#

