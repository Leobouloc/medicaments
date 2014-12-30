# -*- coding: utf-8 -*-
"""
Created on Tue Dec 16 14:46:29 2014

@author: debian
"""

annees = [['20' + str(an).zfill(2) + str(mois).zfill(2) for mois in range(1,13)] 
            for an in range(3,14)]


def cout(table_groupe, period):
    period_prix_par_ddd = ['prix_par_ddd_' + x for x in period]
    period_ddd_rembourse = ['ddd_rembourse_' + x for x in period]
    vol = table_groupe[period_ddd_rembourse]
    prix = table_groupe[period_prix_par_ddd]
    vol.columns = period
    prix.columns = period
    return (vol * prix).sum().sum()

def cout_min(table_groupe, period):
    period_prix_par_ddd = ['prix_par_ddd_' + x for x in period]
    period_ddd_rembourse = ['ddd_rembourse_' + x for x in period]
    vol = table_groupe[period_ddd_rembourse]
    prix = table_groupe[period_prix_par_ddd]
    vol.columns = period
    prix.columns = period
    prix_min = prix.min()
    assert (prix_min != 0).all()
    return (vol * prix_min).sum().sum()
    
def diff_cout_prop(table_groupe, period):
    c = cout(table_groupe, period)
    c_m = cout_min(table_groupe, period)
    return (c-c_m)/c
    
#sbase = base[base['selector_cip']]
c = sbase.groupby('Id_Groupe').apply(lambda x: cout(x, period)).sum()
c_m = sbase.groupby('Id_Groupe').apply(lambda x: cout_min(x, period)).sum() # Cout si on payait le moins cher du groupe
diff = c - c_m
#diff_prop = diff / c

#c = [sbase.groupby('Id_Groupe').apply(cout, annee).sum() for annee in annees]
#c_m = [sbase.groupby('Id_Groupe').apply(cout_min, annee).sum() for annee in annees]
#diff_annuelle = [x-y for (x, y) in zip(c, c_m)]
#diff_annuelle_prop = [x / y for (x, y) in zip(diff_annuelle, c)]

# Proportion du pris composé des dépenses additionelles liées au non médicament non maximal
#diff_prop_atc = sbase.groupby('CODE_ATC_1').apply(lambda x: x.groupby('Id_Groupe').apply(lambda y : (cout(y, period) - cout_min(y, period))).sum() / x.groupby('Id_Groupe').apply(lambda y: cout(y, period)).sum())

# On genere ATC_1
#sbase.loc[sbase['CODE_ATC'].notnull(), 'CODE_ATC_1'] = sbase.loc[sbase['CODE_ATC'].notnull(), 'CODE_ATC'].apply(lambda x: x[0])