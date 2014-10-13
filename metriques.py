# -*- coding: utf-8 -*-
"""
Created on Mon Oct 13 10:14:27 2014

@author: work
"""

def prix_moyen(table_groupe, average_over=12, prix='prix', selection='princeps'):
    '''Renvoie simplement le prix moyen des princeps (avant la chute), ou des génériques'''
    assert prix in ['prix_par_dosage', 'prix']
    assert selection in ['generiques', 'princeps']
    
    if prix == 'prix_par_dosage':
        var_prix = period_prix_par_dosage
    elif prix == 'prix':
        var_prix = period_prix
        
    date_chute = table_groupe.loc[~table_groupe['role'],'premiere_vente'].min() 

    if not np.isnan(date_chute):
        if selection == 'princeps':
            table_groupe_princeps = table_groupe[table_groupe['Type'] == 0]
            chute_moins = period.index(date_chute) - average_over
            moyenne_avant = table_groupe_princeps[var_prix].iloc[:, range(chute_moins, chute_moins + average_over)].mean().mean()
            return(moyenne_avant)
        elif selection == 'generiques':
            table_groupe_generique = table_groupe[table_groupe['Type'] != 0]
            generique = table_groupe_generique[var_prix].iloc[:, period.index(date_chute)].mean()
            return generique
    else:
        return np.nan
    
def volume_chute_brevet(table_groupe, average_over=12, span = 0):
    '''Calcule la variation relative de volume sur un an avant et après la chute de brevet pour le groupe'''
    date_chute = table_groupe.loc[~table_groupe['role'],'premiere_vente'].min()
    if not np.isnan(date_chute):
        chute_moins = period.index(date_chute) - average_over - span
        chute_plus = period.index(date_chute) + average_over + span
        if chute_moins >= 0 and chute_plus <= len(period):
            somme_avant = table_groupe[period_dosage_rembourse].iloc[:, range(chute_moins, chute_moins + average_over)].sum().mean()  
            somme_apres = table_groupe[period_dosage_rembourse].iloc[:, range(chute_plus - average_over, chute_plus)].sum().mean()
            variation = (somme_apres - somme_avant) / somme_avant
            return variation
        else:
            return np.nan
    else:
        return np.nan

def prix_chute_brevet(table_groupe, average_over=12, prix = 'prix_par_dosage', selection = 'groupe'):
    '''Calcule la variation relative de prix pour un an avant et après la chute de brevet pour le groupe'''
    '''selection = "groupe" : ecart relatif du prix moyen des médicaments du groupe avant et après la chute'''
    '''selection = "princeps" : ecart relatif du prix moyen des princeps avant et après la chute'''
    '''selection = "ecart princeps_generique" : ecart de prix entre le princeps et les génériques mis sur le marché'''
    assert prix in ['prix_par_dosage', 'prix']
    assert selection in ['groupe', 'princeps', 'ecart_princeps_generique']
    
    date_chute = table_groupe.loc[~table_groupe['role'],'premiere_vente'].min()    
    
    if prix == 'prix_par_dosage':
        var_prix = period_prix_par_dosage
    elif prix == 'prix':
        var_prix = period_prix
        
    if selection == 'princeps':
        table_groupe = table_groupe[table_groupe['Type'] == 0]

    if not np.isnan(date_chute):
        chute_moins = period.index(date_chute) - average_over
        chute_plus = period.index(date_chute) + average_over
        if selection in ['groupe', 'princeps']:
            if chute_moins >= 0 and chute_plus <= len(period):
                moyenne_avant = table_groupe[var_prix].iloc[:, range(chute_moins, chute_moins + average_over)].sum().mean()
                moyenne_apres = table_groupe[var_prix].iloc[:, range(chute_plus - average_over, chute_plus)].sum().mean()
                variation = (moyenne_apres - moyenne_avant) / moyenne_avant
                return variation
        elif selection in ['ecart_princeps_generique']:
            if chute_moins >= 0:
                table_groupe_princeps = table_groupe[table_groupe['Type'] == 0]
                table_groupe_generique = table_groupe[table_groupe['Type'] != 0]
                # Renvoie l'écart relatif entre la moyenne un an avant la chute du princeps et le prix moyen des génériques lors de la chute
                moyenne_princeps_avant = table_groupe_princeps[var_prix].iloc[:, range(chute_moins, chute_moins + average_over)].mean().mean()             
                generique = table_groupe_generique[var_prix].iloc[:, period.index(date_chute)].mean()
                variation = (generique - moyenne_princeps_avant) / moyenne_princeps_avant
                return variation
            else:
                return np.nan
        else:
            return np.nan
    else:
        return np.nan        

def labo_princeps(table_groupe):
    labo = table_groupe.loc[table_groupe['Type'] == 0, 'LABO']
    if len(labo) != 0:
        return(labo.iloc[0])
    else:
        return np.nan

def labo_to_int(serie):

    labos = list(set(base_brute['LABO']))
    def function(x):  
        if isinstance(x, float):
            return np.nan
        else: 
            return labos.index(x)
    return serie.apply(lambda x: function(x))
    