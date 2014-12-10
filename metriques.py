# -*- coding: utf-8 -*-
"""
Created on Mon Oct 13 10:14:27 2014

@author: work
"""
import pandas as pd
import scipy
from tools.panda_tools import panda_merge


global somme_classe
somme_classe = base.groupby('CODE_ATC')[period_nb_dj_rembourse].sum()


def is_me_too(table_classe):
    def temporaire(x):
        x = x.dropna()
        if len(x) == 0:
            return np.nan
        else:
            print x
            return x.iloc[0]

    ''' renvoie les Id groupes des me-too (sans considération de l'ASMR)'''
    group_start = table_classe.groupby('Id_Groupe')['premiere_vente'].min() # Premiere vente pour chaque groupe la classe
    group_asmr = table_classe.groupby('Id_Groupe')['Valeur_ASMR'].apply(temporaire)
    class_start = group_start.min()
    later_groups = list(group_start.index[(group_start != class_start) & group_asmr])
    return later_groups


def lambda_func(ligne):
    '''renvoie le CIP7 si c'est un me-too, 0 sinon'''
    if ligne['Valeur_ASMR'] == 'V' and (not ligne['premier_de_la_classe']) and ligne['Type'] == 0:
        return ligne['CIP7']
    else:
        return 0


def nb_groupes(table, Id_Groupe, when = 'avant'):
    '''Renvoie le nombre de groupes prééxistants dans la classe avant la mise en vente d'un médicament défini par ligne'''
    code_atc = table.loc[table['Id_Groupe'] == Id_Groupe, 'CODE_ATC_4'].iloc[0]
    date = table.loc[table['Id_Groupe'] == Id_Groupe, 'premiere_vente'].min()
    table2 = table[table['CODE_ATC_4'] == code_atc]
    if when == 'avant':
        selector = table2['premiere_vente'] < date
    elif when == 'apres':
        selector = table2['premiere_vente'] >= date
    nb_groupes = table2.loc[selector, 'Id_Groupe'].nunique()
    return nb_groupes


#ventes_par_groupe = base_brute.groupby('Id_Groupe')[period_nb_dj_rembourse].sum().sum(axis = 1)
#code_par_groupe = base_brute.groupby('Id_Groupe')['CODE_ATC_4'].first()
#test = panda_merge(code_par_groupe, ventes_par_groupe)
#test.columns = ['CODE_ATC_4', 'ventes']
#rank_par_groupe = test.groupby('CODE_ATC_4').rank(ascending = False)

#index = pd.Series(base_brute.index, index = base_brute.index)
#index.apply(lambda x: lambda_func(base_brute, x))
#
#is_me_too = index.apply(lambda x: lambda_func(base_brute, x))


def periodogramme(table_group, average_over = 12):
    '''fait les transfo de Fourier, spectre des ventes'''
    print table_group['Id_Groupe'].iloc[0]
    test = table_group[period] - moving_average(table_group[period], average_over)
    test = test.sum()
    test.dropna(inplace = True)
    f, Pxx_spec = signal.periodogram(test, 1, 'flattop', scaling='spectrum')
    return f, Pxx_spec

#test = base_brute.groupby('Id_Groupe').apply(periodogramme


def plot_periodogramme(result, Id_Groupe):
    f = result.loc[Id_Groupe][0]
    Pxx_spec = result.loc[Id_Groupe][1]
    plt.plot(f, Pxx_spec)
    plt.show()


def variabilite(table, what = 'rms'): #Pour répérer les médicaments saisonniers
    import math
    season_len = 4
    def regularite_lambda(ligne_var):
        "renvoie la moyenne des std des variabilités pour chaque mois"
        std_sum = 0
        for month in range(0, 12):
            period_month = [period[i] for i in range(0, len(period)) if i % 12 == month]
            std = ligne_var[period_month].std()
            std_sum += std
        return std_sum / 12

    '''Somme des écarts absolus à la moyenne annuelle normalisé par rapport au total consomme'''
    moyenne = moving_average(table[period])
    table_saison = moving_average(table[period], season_len)
    difference = table_saison - moyenne
    variabilite = difference / moyenne
    if what == 'rms':
        variabilite = variabilite.applymap(lambda x: x**2).sum(axis=1).apply(math.sqrt)
        return variabilite
    elif what == 'std':
        regularite_de_la_variabilite = variabilite.apply(regularite_lambda, axis=1)
        return regularite_de_la_variabilite


def table_de_variabilite(base_brute, grouper_par = 'Id_Groupe'):
    '''Renvoie une table avec les champs : var (variabilite : plus c'est grand, plus on varie à la moyenne)
                                           reg (plus reg est petit, plus on est regulier)
                                           var_sur_reg (plus c'est grand, plus la probabilité d'être saisonnier est grande)'''
    print 'attention, ca va etre long...'
    reg = base_brute.groupby(grouper_par).apply(lambda x: variabilite(x, what = 'std').mean())
    print 'encore plus long...'
    var = base_brute.groupby(grouper_par).apply(lambda x: variabilite(x, what = 'rms').mean())
    test = panda_merge(var, reg)
    test.columns = ['var', 'reg']
    test['var_sur_reg'] = test['var']/test['reg']
    test = test.sort('var_sur_reg').dropna(how = 'any')
    return test


def plusieurs_labos_par_princeps(table_groupe):
    labos = table_groupe.loc[table_groupe['Type'] == 0, 'LABO']
    return len(set(labos))


def nombre_de_nouveaux_princeps(table_groupe, duree=12, niveau_atc = 4, sel_labo = True):
    '''determine le nombre de princeps du même labo qui apparaissent dans les
        12 mois (duree) autour de la date de chute dans la même classe'''
    '''sel_labo = True contraint les nouveaux princeps a être faits par le même Labo'''
    if niveau_atc == 4:
        string_atc = 'CODE_ATC_4'
    elif niveau_atc == 5 or niveau_atc == 6:
        string_atc = 'CODE_ATC'

    classe = table_groupe[string_atc].iloc[0]
    groupe = table_groupe['Id_Groupe'].iloc[0]

    # On prend  comme labo de référence celui qui commercialise le princeps en premier
    if sel_labo:
        labo = labo_princeps(table_groupe)

    # On détermine la date de chute du brevet pour le groupe concerné
    date_chute = table_groupe.loc[~table_groupe['role'], 'premiere_vente'].min()
    if date_chute == 200301:
        return np.nan
    elif not np.isnan(date_chute):
        index_date_chute = period.index(date_chute)
        # On selectionne les princeps de la même classe, de groupes différents et du même Labo
        table = base_brute
        table = table[table[string_atc] == classe]
        table = table[table['Id_Groupe'] != groupe]
        selector1 = table.groupby('Id_Groupe')['premiere_vente'].apply(lambda x: x.argmin())
        table = table.loc[selector1]
        if sel_labo:
            table = table[table['LABO'] == labo]
        table = table[table['Type'] == 0]

        # On sélectionne les medicaments qui sont mis en vente autour de la chute du brevet
        def temporaire(x):
            return abs(period.index(x) - index_date_chute) <= duree and period.index(x) != 0
        selector = table['premiere_vente'].apply(temporaire)
        table = table.loc[selector]
#        return [len(set(table['Id_Groupe'])), table['Id_Groupe']]
        return len(set(table['Id_Groupe']))

    else:
        return np.nan


def vol_abs_chute_brevet(table_groupe, average_over=12, span = 0, center = 0, proportion = False, somme_classe = somme_classe):
    date_chute = table_groupe.loc[table_groupe['Type'] != 0, 'premiere_vente'].min()
    if date_chute != 200301:
        return volume_moyen(table_groupe, date_chute, average_over=12, selection='princeps', proportion = proportion, somme_classe = somme_classe)
    else:
        return np.nan


def volume_moyen(table_groupe, date, average_over=12, selection='princeps', proportion = False, somme_classe = somme_classe):
    '''Renvoie simplement le volume moyen des princeps (avant la chute), ou des génériques (sur toute la période)'''
    assert selection in ['generiques', 'princeps']

    if not isinstance(date, float):
        if selection == 'princeps':
            table_groupe_princeps = table_groupe[table_groupe['Type'] == 0]
            chute_moins_a = period.index(date) - average_over
            chute_moins_a = max(0, chute_moins_a)
            chute_moins_b = min(chute_moins_a + average_over, len(period))

            moyenne_avant = table_groupe_princeps[period_nb_dj_rembourse].iloc[:, range(chute_moins_a, chute_moins_b)].mean().mean()

            if proportion:
                code_atc = table_groupe['CODE_ATC'].iloc[0]
                moyenne_avant_classe = somme_classe.loc[code_atc, :].iloc[range(chute_moins_a, chute_moins_b)].mean()
                return moyenne_avant/moyenne_avant_classe
            else:
                return(moyenne_avant)
        elif selection == 'generiques':
            table_groupe_generique = table_groupe[table_groupe['Type'] != 0]
            generique = table_groupe_generique[period_nb_dj_rembourse].iloc[:, period.index(date_chute)].mean()
            if proportion:
                code_atc = table_groupe['CODE_ATC'].iloc[0]
                moyenne_avant_classe = somme_classe.loc[code_atc, :].iloc[range(chute_moins, chute_moins + average_over)].mean()
                return generique/moyenne_avant_classe
            return generique
    else:
        return np.nan


def prix_moyen(table_groupe, average_over=12, prix='prix', selection='princeps', somme_classe = somme_classe):
    '''Renvoie simplement le prix moyen des princeps (avant la chute), ou des génériques'''
    assert prix in ['prix_par_dj', 'prix']
    assert selection in ['generiques', 'princeps']

    if prix == 'prix_par_dj':
        var_prix = period_prix_par_dj
    elif prix == 'prix':
        var_prix = period_prix

    date_chute = table_groupe.loc[~table_groupe['role'],'premiere_vente'].min()

    if not isinstance(date_chute, float):
        if selection == 'princeps':
            table_groupe_princeps = table_groupe[table_groupe['Type'] == 0]
            chute_moins_a = period.index(date_chute) - average_over
            chute_moins_a = max(0, chute_moins_a)
            chute_moins_b = min(chute_moins_a + average_over, len(period))
            moyenne_avant = table_groupe_princeps[var_prix].iloc[:, range(chute_moins_a, chute_moins_b)].mean().mean()
            return(moyenne_avant)
        elif selection == 'generiques':
            table_groupe_generique = table_groupe[table_groupe['Type'] != 0]
            generique = table_groupe_generique[var_prix].iloc[:, period.index(date_chute)].mean()
            return generique
    else:
        return np.nan


def volume_chute_brevet(table_groupe, average_over=12, span = 0, center = 0, relatif_a_la_classe = False, somme_classe = somme_classe):
    date_chute = table_groupe.loc[table_groupe['Type'] != 0,'premiere_vente'].min()
    return var_volume(table_groupe, date_chute, average_over, span, center, relatif_a_la_classe, somme_classe)


def volume_entree_princeps_lambda(base_brute, Id_Groupe):
    '''Variation de volume de sa classe lors de l'entrée sur le marché du médicament défini par ligne'''
    date = base_brute.loc[base_brute['Id_Groupe'] == Id_Groupe, 'premiere_vente'].min()
    if not isinstance(date, float) and date != '200301':
        string_select = 'CODE_ATC_4'
        code_atc = base_brute.loc[base_brute['Id_Groupe'] == Id_Groupe, string_select].iloc[0]
        table_classe = base_brute[base_brute[string_select] == code_atc]
        var_vol = var_volume(table_classe, date, average_over=12, span =2, center = 0, relatif_a_la_classe = False, somme_classe = somme_classe)
        return var_vol
    else:
        return np.nan


def var_volume(table_groupe, date, average_over=12, span = 0, center = 0, relatif_a_la_classe = False, somme_classe = somme_classe):
    '''Calcule la variation relative de volume sur un an avant et après la chute de brevet pour le groupe'''
    '''Proportion = True renvoie la variation par rapport au volume de la classe'''
    '''Span : écart additionnel au centre'''
    '''Center : centre de la moyenne (par défaut la chute du brevet)'''
#    if not np.isnan(date):
    if not isinstance(date, float):
        # variations entre chute_moins_a et chute_moins_b // et // chute_plus_a et chute_plus_b
        chute_moins_a = period.index(date) - average_over - span + center
        chute_plus_b = period.index(date) + average_over + span + center
        chute_moins_a = max(0, chute_moins_a)
        chute_plus_b = min(chute_plus_b, len(period))
        chute_moins_b = min(chute_moins_a + average_over, len(period))
        chute_plus_a = max(0, chute_plus_b - average_over)
        
        if chute_plus_a <= chute_moins_b: # On vérifie que les plages ne se recoupent pas
            return np.nan
        if chute_plus_a == chute_plus_b or chute_moins_a == chute_moins_b:
            return np.nan

        somme_avant = table_groupe[period_nb_dj_rembourse].iloc[:, range(chute_moins_a, chute_moins_b)].sum().sum()
        somme_apres = table_groupe[period_nb_dj_rembourse].iloc[:, range(chute_plus_a, chute_plus_b)].sum().sum()

        if relatif_a_la_classe:
            code_atc = table_groupe['CODE_ATC'].iloc[0]
#                diviseur_avant = somme_classe_avant.loc[code_atc, :].iloc[range(chute_moins, chute_moins + average_over)]
#                diviseur_apres = somme_apres / somme_classe_apres.loc[code_atc, :].iloc[range(chute_plus - average_over, chute_plus)]
            somme_avant = somme_avant / somme_classe.loc[code_atc, :].iloc[range(chute_moins_a, chute_moins_a)].sum()
            somme_apres = somme_apres / somme_classe.loc[code_atc, :].iloc[range(chute_plus_a, chute_plus_b)].sum()
            '''On renvoie la variation absolue en proportion'''
            return (somme_apres - somme_avant)

        variation = (somme_apres - somme_avant) / somme_avant
        return variation
    else:
        return np.nan
#test = base_brute[base_brute['Type'] == 0].apply(lambda x: volume_entree_princeps_lambda(base_brute, x), axis = 1)


def prix_chute_brevet(table_groupe, average_over=12, prix = 'prix_par_dj', selection = 'groupe', span=6):
   date_chute = table_groupe.loc[~table_groupe['role'],'premiere_vente'].min()
   return var_prix(table_groupe, date_chute, average_over=12, prix = 'prix_par_dj', selection = 'groupe', span=6)


def var_prix(table_groupe, date, average_over=12, prix = 'prix_par_dj', selection = 'groupe', span = 0, center = 0,):
    '''Calcule la variation relative de prix pour un an avant et après la chute de brevet pour le groupe'''
    '''selection = "groupe" : ecart relatif du prix moyen des médicaments du groupe avant et après la chute'''
    '''selection = "princeps" : ecart relatif du prix moyen des princeps avant et après la chute'''
    '''selection = "ecart princeps_generique" : ecart de prix entre le princeps et les génériques mis sur le marché'''
    assert prix in ['prix_par_dj', 'prix'] # C'est bê te, c'est pareil (??)
    assert selection in ['groupe', 'princeps', 'ecart_princeps_generique']

    if prix == 'prix_par_dj':
        var_prix = period_prix_par_dosage
    elif prix == 'prix':
        var_prix = period_prix

    if selection == 'princeps':
        table_groupe = table_groupe[table_groupe['Type'] == 0]

    if not isinstance(date, float):
        # variations entre chute_moins_a et chute_moins_b // et // chute_plus_a et chute_plus_b
        chute_moins_a = period.index(date) - average_over - span + center
        chute_plus_b = period.index(date) + average_over + span + center
        chute_moins_a = max(0, chute_moins_a)
        chute_plus_b = min(chute_plus_b, len(period))
        chute_moins_b = min(chute_moins_a + average_over, len(period))
        chute_plus_a = max(0, chute_plus_b - average_over)

        if chute_plus_a <= chute_moins_b: # On vérifie que les plages ne se recoupent pas
            return np.nan
        if selection in ['groupe', 'princeps']:
            moyenne_avant = table_groupe[var_prix].iloc[:, range(chute_moins_a, chute_moins_b)].sum().mean()
            moyenne_apres = table_groupe[var_prix].iloc[:, range(chute_plus_a, chute_plus_b)].sum().mean()
            variation = (moyenne_apres - moyenne_avant) / moyenne_avant
            return variation

        elif selection in ['ecart_princeps_generique']:
            table_groupe_princeps = table_groupe[table_groupe['Type'] == 0]
            table_groupe_generique = table_groupe[table_groupe['Type'] != 0]
            # Renvoie l'écart relatif entre la moyenne un an avant la chute du princeps et le prix moyen des génériques lors de la chute
            moyenne_princeps_avant = table_groupe_princeps[var_prix].iloc[:, range(chute_moins_a, chute_moins_b)].mean().mean()
            generique = table_groupe_generique[var_prix].iloc[:, period.index(date_chute)].mean()
            variation = (generique - moyenne_princeps_avant) / moyenne_princeps_avant
            return variation

        else:
            return np.nan
    else:
        return np.nan


def is_new(table_groupe):
    date = table_groupe['premiere_vente'].min()
    if date == 200301:
        return 'no'
    else:
        return 'yes'


def labo_princeps(table_groupe):
    '''Renvoie le labo qui a produit le princeps le plus ancien du groupe'''
    try:
        index_princeps = table_groupe.loc[table_groupe['Type'] == 0, 'premiere_vente'].argmin()
        labo = table_groupe[table_groupe['Type'] == 0].loc[index_princeps, 'LABO']
        return labo
    except:
        if not any(table_groupe['Type'] == 0):
            labo = np.nan#'princeps inconnu'
        else:
            print 'in else'
            labo = table_groupe[table_groupe['Type'] == 0].iloc[0]['LABO']
        return labo


def labo_to_int(serie):
    labos = list(set(base_brute['LABO']))
    def _function(x):
        if isinstance(x, float):
            return np.nan
        else:
            return labos.index(x)
    return serie.apply(_function)


def taux_rembours_float(string):
    if string == '65 %':
        return 0.65
    elif string == '30 %':
        return 0.30
    elif string == '15 % ':
        return 0.15
    elif string == '100 %':
        return 1
    else:
        return np.nan

#nombre_de_labos_par_groupe = base_brute.groupby('Id_Groupe').apply(lambda x: x['LABO'].nunique())
#nombre_de_generiques_par_groupe = base_brute.groupby('Id_Groupe').apply(lambda x: x.loc[x['Type']!=0, 'LABO'].nunique())

#a=base_brute.groupby('CODE_ATC_4').apply(is_me_too).values
#a = list(a)
#
#while 0 in a:
#    a.remove(0)
#selector = base_brute['CIP7'].apply(lambda x: x in a)
#var_vol_me_too = base_brute[selector].apply(lambda x: volume_entree_princeps_lambda(base_brute, x), axis = 1)
#base_brute = base_brute.merge(pd.DataFrame(var_vol_me_too, columns = ['var_vol_me_too']), how = 'left', left_index = True, right_index = True)
#
#base_brute['nb_groupes_anterieurs'] = np.nan
## var_vol_me_too
#base_brute['nb_groupes_anterieurs'] = base_brute[base_brute['var_vol_me_too'].notnull()].apply(lambda x: nb_groupes_avant(base_brute, x), axis = 1)

try:
    var_vol
except:
    
    
    full[period_nb_dj_rembourse] = full[period_nb_dj_rembourse].replace(0, np.nan)
    full = full[full[period_nb_dj_rembourse].notnull().any(axis = 1)]
    
    '''Pour chaque groupe : variation relative de volume entre l année précédent la chute et l année suivante'''
    var_vol = full.groupby('Id_Groupe').apply(lambda x: volume_chute_brevet(x, average_over = 12, span = 10, relatif_a_la_classe = False))
    #var_vol = var_vol[var_vol.apply(lambda x: abs(x))<10] ### On ne garde que les variations 'normales'
    #'''Pour chaque groupe : variation relative de prix entre l année précédent la chute et l année suivante'''
    var_prix = full.groupby('Id_Groupe').apply(lambda x: prix_chute_brevet(x, average_over = 12, span = 10, selection='ecart_princeps_generique'))

    vol = full.groupby('Id_Groupe').apply(lambda x: vol_abs_chute_brevet(x, average_over=12, span = 0, center = 0, proportion = False, somme_classe = somme_classe))
    prix = full.groupby('Id_Groupe').apply(lambda x: prix_moyen(x, average_over=12, selection='princeps', prix='prix_par_dj'))

    taux_rembours = full.groupby('Id_Groupe')['Taux_rembours'].apply(lambda x: x.iloc[0])

    var_vol.name = 'var_vol'
    var_prix.name = 'var_prix'
    vol.name = 'vol'
    prix.name = 'prix'
    taux_rembours.name = 'taux_rembours'

    '''Visualisation de la distribution des variations de prix'''
    # plt.hist(list(testo[~testo.isnull()]), bins = 20)
    # plt.show()

    '''Nombre de labos par princeps'''
    #nb_labos_par_princeps = base_brute.groupby('Id_Groupe').apply(lambda x: plusieurs_labos_par_princeps(x))
    '''Nombre de labos par groupe'''
    #nb_labos_par_groupe = base_brute.groupby('Id_Groupe').apply(lambda x: x['LABO'].nunique())

    '''Voir pour quels groupes la chute du brevet entraine un nouveau groupe dans la même classe par le même labo'''
#    nb_nouveaux_princeps = base_brute.groupby('Id_Groupe').apply(lambda x : nombre_de_nouveaux_princeps(x, sel_labo=False, duree = 20))
#    nb_nouveaux_princeps = base_brute.groupby('Id_Groupe').apply(lambda x : x['C'])
#    code_du_groupe = base_brute.groupby('Id_Groupe').CODE_ATC.apply(lambda x: x.iloc[0])
#    nb_nouveaux_princeps = nb_nouveaux_princeps[nb_nouveaux_princeps != (-1,0)]
#    nb_nouveaux_princeps = nb_nouveaux_princeps[nb_nouveaux_princeps.apply(lambda x: x[0] != 0)]
#
    '''Visualisation : variation de volume en fonction du nombre de labos créant des princeps (par ex)'''
    #test = pd.merge(pd.DataFrame(nb_labos_par_princeps), pd.DataFrame(testo), left_index = True, right_index = True, how='inner')
    #test = pd.merge(test, pd.DataFrame(code_du_groupe), left_index = True, right_index = True, how='inner')
    #plt.scatter(test.iloc[:,0], test.iloc[:,1])
    #plt.show()

    '''repérage des me-too'''
    a = full.groupby('CODE_ATC_4').apply(is_me_too)
    me_too = a.sum()
    # variation du volume de la classe
    var_vol_me_too = pd.Series([volume_entree_princeps_lambda(full, x) for x in me_too], index = me_too)
    #me_toos = base_brute[base_brute['Id_Groupe'].apply(lambda x: x in me_too)] # restriction de base_brute aux me-too
    #var_vol_me_too = me_toos.apply(lambda x: volume_entree_princeps_lambda(base_brute, x), axis=1)
    nombre_princeps = pd.Series([nb_groupes(full, x, when = 'avant') for x in me_too], index = me_too)

