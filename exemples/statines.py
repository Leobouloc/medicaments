

# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 22:37:37 2014

@author: alexis
"""
import matplotlib.pyplot as plt

from exploitation_sniiram import get_base_brute
from display_and_graphs import graph_volume_classe, display_classe
from outils import all_periods

base_brute = get_base_brute()


statine = base_brute[base_brute['CODE_ATC_4'] == "C10AA"]
statine['Id_Groupe'].value_counts(dropna=False)
statine['premiere_vente'].value_counts(dropna=False)
statine['premiere_vente'].hist(bins=50)
statine['premiere_vente'].hist(by=statine['Id_Groupe'], bins=50)


# TODO: select 1 ASMR

statine.CIP.value_counts()
# on prend un groupe
grp = statine[statine['Id_Groupe'] == 915]
grp.iloc[:, :30]

test = statine.groupby('Id_Groupe').sum()
test[all_periods(statine)[3]].T.plot()
statine.sum()[all_periods(statine)[3]].T.plot()

test = statine.groupby(['CODE_ATC','role']).sum()
test[all_periods(statine)[0]].T.plot()

statine[all_periods(statine)[0]].T.plot()
statine[all_periods(statine)[0]].sum().plot()
plt.show()



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


display_classe(statine.drop_duplicates('CIP'), input_val="C10AA", 
               sum_by=['Id_Groupe','role'], display='volume')
                    
graph_volume_classe(statine.drop_duplicates('CIP'), input_val="C10AA",
                    display='volume', make_sum=False)
                  
graph_volume_classe(statine.drop_duplicates('CIP'), input_val="C10AA",
                    display='volume', make_sum=True)
graph_volume_classe(base_brute, input_val="C10AA05", make_sum=True)

#import display_and_graphs as dis
#dis.graph_prix_classe('C10AA')
#graph_volume_classe(CODE_ATC="C10AA05")
#

