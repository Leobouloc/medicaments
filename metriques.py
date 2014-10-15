# -*- coding: utf-8 -*-
"""
Created on Mon Oct 13 10:14:27 2014

@author: work
"""

def plusieurs_labos_par_princeps(table_groupe):
    labos = table_groupe.loc[table_groupe['Type'] == 0, 'LABO']
    return len(set(labos))


def nombre_de_nouveaux_princeps(table_groupe, duree=12, niveau_atc = 4):
    '''determine le nombre de princeps du même labo qui apparaissent dans les
        12 mois (duree) autour de la date de chute'''
    if niveau_atc == 4:
        string_atc = 'CODE_ATC_4'
    elif niveau_atc == 5 or niveau_atc == 6:
        string_atc = 'CODE_ATC'

    classe = table_groupe[string_atc].iloc[0]
    groupe = table_groupe['Id_Groupe'].iloc[0]

    # On prend  comme labo de référence celui qui commercialise le princeps en premier
    labo = labo_princeps(table_groupe)

    # On détermine la date de chute du brevet pour le groupe concerné
    date_chute = table_groupe.loc[~table_groupe['role'], 'premiere_vente'].min()
    if date_chute == 200301:
        return (-1, 0)
    elif not np.isnan(date_chute):
        index_date_chute = period.index(date_chute)
        # On selectionne les princeps de la même classe, de groupes différents et du même Labo
        table = base_brute
        table = table[table[string_atc] == classe]
        table = table[table['Id_Groupe'] != groupe]
        selector1 = table.groupby('Id_Groupe')['premiere_vente'].apply(lambda x: x.argmin())
        table = table.loc[selector1]
        table = table[table['LABO'] == labo]
        table = table[table['Type'] == 0]

        # On sélectionne les medicaments qui sont mis en vente autour de la chute du brevet
        def temporaire(x):
            return abs(period.index(x) - index_date_chute) <= duree and period.index(x) != 0
        selector = table['premiere_vente'].apply(lambda x: temporaire(x))
        table = table.loc[selector]
        return [len(set(table['Id_Groupe'])), table['Id_Groupe']]

    else:
        return (-1, 0)


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
    '''Renvoie le labo qui a produit le princeps le plus ancien du groupe'''
    try:
        index_princeps = table_groupe.loc[table_groupe['Type'] == 0, 'premiere_vente'].argmin()
        labo = table_groupe[table_groupe['Type'] == 0].loc[index_princeps, 'LABO']
        return labo
    except:
        if not any(table_groupe['Type'] == 0):
            labo = 'princeps inconnu'
        else:
            print 'in else'
            labo = table_groupe[table_groupe['Type'] == 0].iloc[0]['LABO']
        return labo
    
def labo_to_int(serie):

    labos = list(set(base_brute['LABO']))
    def function(x):
        if isinstance(x, float):
            return np.nan
        else:
            return labos.index(x)
    return serie.apply(lambda x: function(x))

testo = base_brute.groupby('Id_Groupe').apply(lambda x: volume_chute_brevet(x, average_over = 12, span = 6))
testu = testo[testo.apply(lambda x: abs(x))<1]
plt.hist(list(testu[~testu.isnull()]), bins = 20)
plt.show()

#nb_labos_par_princeps = base_brute.groupby('Id_Groupe').apply(lambda x: plusieurs_labos_par_princeps(x))

'''Voir pour quels groupes la chute du brevet entraine un nouveau groupe dans la même classe par le même labo'''
nb_nouveaux_princeps = base_brute.groupby('Id_Groupe').apply(lambda x : nombre_de_nouveaux_princeps(x))
nb_nouveaux_princeps = nb_nouveaux_princeps[nb_nouveaux_princeps != (-1,0)]
nb_nouveaux_princeps = nb_nouveaux_princeps[nb_nouveaux_princeps.apply(lambda x: x[0] != 0)]

