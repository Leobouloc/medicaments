# -*- coding: utf-8 -*-
"""
Created on Thu Nov 27 22:13:07 2014

@author: alexis
"""


def all_periods(base_brute):
    ''' fait tout le boulot sur les periods '''
    period = [str(x) for x in base_brute.columns if isinstance(x, long) or x[:2] in ['19', '20']]
    # period_prix renvoie vers les colonnes qui décrivent le prix des medicaments
    period_prix = ['prix_' + x for x in period]
    assert len(period_prix) == len(period)
    assert len([x for x in period_prix if x not in base_brute.columns]) == 0
    period_prix_par_dosage = ['prix_par_dosage_' + str(date) for date in period]
    period_ddd_rembourse = ['ddd_rembourse_' + str(date) for date in period]
    period_prix_par_ddd = ['prix_par_ddd_' + str(date) for date in period]
    return period, period_prix, period_prix_par_dosage, period_ddd_rembourse, period_prix_par_ddd