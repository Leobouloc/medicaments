# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 22:37:37 2014

@author: alexis
"""
import matplotlib.pyplot as plt

from select_base import get_base_selected
from display_and_graphs import graph_volume_classe, display_classe
from outils import all_periods

<<<<<<< HEAD
base = get_base_selected(force = False)
base_copy = base
=======
base = get_base_selected()
>>>>>>> 5b7f49a3457abae2e19472c88adbb60d453e1a76
base = base[base['selector_cip']]

statine = base[base['CODE_ATC_4'].isin(["C10AA",'C10BA', 'C10BX'])]
#  C10AA HMG CoA reductase inhibitors
#  C10BA HMG CoA reductase inhibitors in combination with other lipid modifying agents
#  C10BX HMG CoA reductase inhibitors, other combinations

statine['Id_Groupe'].value_counts(dropna=False)

statine['premiere_vente'].fillna(201600, inplace=True)
statine['premiere_vente'] = statine['premiere_vente'].astype(int)

statine['premiere_vente'].value_counts(dropna=False)
statine['premiere_vente'].hist(bins=50)
statine['premiere_vente'].hist(by=statine['Id_Groupe'], bins=50)


# TODO: ecrire une verification des dosages

statine.loc[:, all_periods(statine)[0]].sum().plot()
# TODO : on vend d'n coup plus de DDD !
statine.loc[:, all_periods(statine)[3]].sum().plot()

statine.loc[:, all_periods(statine)[1]].mean().plot()
statine.loc[:, all_periods(statine)[2]].mean().plot()


# TODO: select 1 ASMR


statine.CIP.value_counts()
# on prend un groupe
grp = statine[statine['Id_Groupe'] == 915]
grp.iloc[:, :30]

statine['Id_Groupe'].fillna(0, inplace=True)
test = statine.groupby('Id_Groupe').sum()
test[all_periods(statine)[3]].T.plot()
statine.sum()[all_periods(statine)[3]].T.plot()

test = statine.groupby('CODE_ATC').sum()
test[all_periods(statine)[3]].T.plot()
statine.sum()[all_periods(statine)[3]].T.plot()

<<<<<<< HEAD
#statine['princeps'] 
=======
test = statine.groupby('CODE_ATC').sum()
test[all_periods(statine)[0]].T.plot()
statine.sum()[all_periods(statine)[0]].T.plot()

>>>>>>> 5b7f49a3457abae2e19472c88adbb60d453e1a76
test = statine.groupby(['CODE_ATC','role']).sum()
test[all_periods(statine)[3]].T.plot()

test = statine.groupby(['CODE_ATC','role']).sum()
test[all_periods(statine)[0]].T.plot()

statine[all_periods(statine)[0]].sum().plot()
plt.show()
statine[all_periods(statine)[0]].T.plot()



probleme = base[base['CODE_ATC'] == "C10AA07"]
#probleme.fillna(0, inplace=True)
probleme[all_periods(statine)[0]].sum().plot()
(probleme[all_periods(statine)[3]].sum()/10).plot()

statine
statine.iloc[:,:10]
sel = gouv.CIP.isnull()
#statine['Code_Substance']
statine['Code_Substance'].value_counts()
statine['Id_Group'].value_counts()
statine['Id_Groupe'].value_counts()
statine = base[base['CODE_ATC'] == "C10AA05"]
statine = base[base['CODE_ATC'] == "C10AA05"]
statine['CIP']

display_classe(statine.drop_duplicates('CIP'), input_val="C10AA", 
               sum_by=['Id_Groupe','role'], display='volume')
                    
graph_volume_classe(statine.drop_duplicates('CIP'), input_val="C10AA",
                    display='volume', make_sum=False)
                  
graph_volume_classe(statine.drop_duplicates('CIP'), input_val="C10AA",
                    display='volume', make_sum=True)
graph_volume_classe(base, input_val="C10AA05", make_sum=True)

#import display_and_graphs as dis
#dis.graph_prix_classe('C10AA')
#graph_volume_classe(CODE_ATC="C10AA05")
#

