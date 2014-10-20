# -*- coding: utf-8 -*-
"""
Created on Mon Oct 13 10:14:27 2014

@author: work
"""

def is_me_too(table_classe):
    group_start = table_classe.groupby('Id_Groupe')['premiere_vente'].min()
    table_classe['premier_de_la_classe'] = table_classe['premiere_vente'].apply(lambda x: x == group_start.min())
    is_me_too = table_classe.apply(lambda x: x['Valeur_ASMR'] == 'V' and not x['premier_de_la_classe'] and x['Type'] == 0, axis=1)
    return is_me_too

### Utilité discutable, ne pas supprimer
#def cout_classe (code_atc):
#    '''Calcul la différence de prix si tous les médicaments étaient remboursés au prix du moins cher dans la classe'''
#    base_classe = base_brute.loc[base_brute['CODE_ATC']==code_atc,:]
#    prix_min_par_dosage=base_classe[period_prix_par_dosage].apply(lambda column: min(column))
#    # On considere que tous les médicaments d'ASMR V peuvent être remplacés par un médicament de la même classe (dosage équivalent) moins cher
#    # On calcule donc la différence de cout pour tous les médicaments d'ASMR V
#    cout = sum(base_classe.loc[base_classe['Valeur_ASMR']=='V',:].apply(lambda x: dot(x.loc[period_dosage_rembourse],(x[period_prix_par_dosage]-prix_min_par_dosage)),axis=1))
#    return cout
#
#def cout_groupe (id_groupe):
#    '''Calcul la différence de prix si tous les médicaments étaient remboursés au prix du moins cher dans le groupe'''
#    base_groupe= base_brute.loc[base_brute['Id_Groupe']==id_groupe,:]
#    prix_min_par_dosage=base_groupe[period_prix_par_dosage].apply(lambda column: min(column))
#    # On considere que tous les médicaments d'ASMR V peuvent être remplacés par un médicament de la même classe (dosage équivalent) moins cher
#    # On calcule donc la différence de cout pour tous les médicaments d'ASMR V
#    cout = sum(base_groupe.loc[base_groupe['Valeur_ASMR']=='V',:].apply(lambda x: dot(x.loc[period_dosage_rembourse],(x[period_prix_par_dosage]-prix_min_par_dosage)),axis=1))
#    return cout
#
#def dot(a,b):
#    assert sum(b.isnull())==0
#    x=a
#    y=b
#    x.index = y.index
#    x_null = x.isnull()
#    x=x[~x_null]
#    y=y[~x_null]
#    return sum(x*y)

def plusieurs_labos_par_princeps(table_groupe):
    labos = table_groupe.loc[table_groupe['Type'] == 0, 'LABO']
    return len(set(labos))


def nombre_de_nouveaux_princeps(table_groupe, duree=12, niveau_atc = 4, sel_labo = True):
    '''determine le nombre de princeps du même labo qui apparaissent dans les
        12 mois (duree) autour de la date de chute'''
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
        selector = table['premiere_vente'].apply(lambda x: temporaire(x))
        table = table.loc[selector]
#        return [len(set(table['Id_Groupe'])), table['Id_Groupe']]
        return len(set(table['Id_Groupe']))

    else:
        return np.nan

def volume_moyen(table_groupe, average_over=12, selection='princeps'):
    '''Renvoie simplement le volume moyen des princeps (avant la chute), ou des génériques'''
    assert selection in ['generiques', 'princeps']

    date_chute = table_groupe.loc[~table_groupe['role'],'premiere_vente'].min()

    if not np.isnan(date_chute):
        if selection == 'princeps':
            table_groupe_princeps = table_groupe[table_groupe['Type'] == 0]
            chute_moins = period.index(date_chute) - average_over
            moyenne_avant = table_groupe_princeps[period_dosage_rembourse].iloc[:, range(chute_moins, chute_moins + average_over)].mean().mean()
            return(moyenne_avant)
        elif selection == 'generiques':
            table_groupe_generique = table_groupe[table_groupe['Type'] != 0]
            generique = table_groupe_generique[period_dosage_rembourse].iloc[:, period.index(date_chute)].mean()
            return generique
    else:
        return np.nan

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
        
somme_classe_avant = base_brute.groupby('CODE_ATC')[period_dosage_rembourse].sum()
somme_classe_apres = base_brute.groupby('CODE_ATC')[period_dosage_rembourse].sum()

def volume_chute_brevet(table_groupe, average_over=12, span = 0, proportion = False, somme_classe_avant = None, somme_classe_apres = None):
    '''Calcule la variation relative de volume sur un an avant et après la chute de brevet pour le groupe'''
    '''Proportion = True renvoie la variation par rapport au volume de la classe'''   

    date_chute = table_groupe.loc[~table_groupe['role'],'premiere_vente'].min()
    if not np.isnan(date_chute):
        chute_moins = period.index(date_chute) - average_over - span
        chute_plus = period.index(date_chute) + average_over + span
        chute_moins = max(0, chute_moins)
        chute_plus = min(chute_plus, len(period))
        if chute_moins >= 0 and chute_plus <= len(period):
            somme_avant = table_groupe[period_dosage_rembourse].iloc[:, range(chute_moins, chute_moins + average_over)].sum().sum()
            somme_apres = table_groupe[period_dosage_rembourse].iloc[:, range(chute_plus - average_over, chute_plus)].sum().sum()

            if proportion:
                code_atc = table_groupe['CODE_ATC'].iloc[0]
#                diviseur_avant = somme_classe_avant.loc[code_atc, :].iloc[range(chute_moins, chute_moins + average_over)]                
#                diviseur_apres = somme_apres / somme_classe_apres.loc[code_atc, :].iloc[range(chute_plus - average_over, chute_plus)]
                                             
                somme_avant = somme_avant / somme_classe_avant.loc[code_atc, :].iloc[range(chute_moins, chute_moins + average_over)].sum()
                somme_apres = somme_apres / somme_classe_apres.loc[code_atc, :].iloc[range(chute_plus - average_over, chute_plus)].sum()
            
            variation = (somme_apres - somme_avant) / somme_avant
            return variation
        else:
            return np.nan
    else:
        return np.nan
        

def prix_chute_brevet(table_groupe, average_over=12, prix = 'prix_par_dosage', selection = 'groupe', span=6):
    '''Calcule la variation relative de prix pour un an avant et après la chute de brevet pour le groupe'''
    '''selection = "groupe" : ecart relatif du prix moyen des médicaments du groupe avant et après la chute'''
    '''selection = "princeps" : ecart relatif du prix moyen des princeps avant et après la chute'''
    '''selection = "ecart princeps_generique" : ecart de prix entre le princeps et les génériques mis sur le marché'''
    assert prix in ['prix_par_dosage', 'prix'] # C'est bête, c'est pareil (??)
    assert selection in ['groupe', 'princeps', 'ecart_princeps_generique']

    date_chute = table_groupe.loc[~table_groupe['role'],'premiere_vente'].min()

    if prix == 'prix_par_dosage':
        var_prix = period_prix_par_dosage
    elif prix == 'prix':
        var_prix = period_prix

    if selection == 'princeps':
        table_groupe = table_groupe[table_groupe['Type'] == 0]

    if not np.isnan(date_chute):
        chute_moins = period.index(date_chute) - average_over - span
        chute_plus = period.index(date_chute) + average_over + span
        chute_moins = max(0, chute_moins)
        chute_plus = min(chute_plus, len(period))
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


def bind_and_plot(serie1, serie2, color_serie = '', describe = '', return_obj = False):
    test = pd.merge(pd.DataFrame(serie1), pd.DataFrame(serie2), left_index = True, right_index = True, how='inner')
    if isinstance(color_serie, str):
        plt.scatter(test['0_x'], test['0_y'])
    else:
        test = pd.merge(test, pd.DataFrame(color_serie), left_index = True, right_index = True, how='inner')
        test.columns = ['0_x', '0_y', '0_z']
        plt.scatter(test['0_x'], test['0_y'], c = test['0_z'])
        plt.gray()
    if describe == 'describe':
        obj = test.groupby('0_x').describe()
    elif describe == 'mean':
        obj = test.groupby('0_x').mean()
    elif describe == 'min_max':
        obj = [test.groupby('0_x').min(), test.groupby('0_x').max()]
    elif describe == 'count':
        obj = test.groupby('0_x').count()
        
    if return_obj:
        plt.show()
        return obj
    elif describe != '':
        print obj
        plt.show()
    else:
        plt.show()
   
def panda_merge(*series):
    test = pd.DataFrame(series[0])
    for i in range(1, len(series)):
        test = pd.merge(test, pd.DataFrame(series[i]), left_index = True, right_index = True, how='inner')
    return test
    
#nombre_de_labos_par_groupe = base_brute.groupby('Id_Groupe').apply(lambda x: x['LABO'].nunique())
#nombre_de_generiques_par_groupe = base_brute.groupby('Id_Groupe').apply(lambda x: x.loc[x['Type']!=0, 'LABO'].nunique())
try:
    var_vol
except: 
    '''Pour chaque groupe : variation relative de volume entre l année précédent la chute et l année suivante'''
    var_vol = base_brute.groupby('Id_Groupe').apply(lambda x: volume_chute_brevet(x, average_over = 12, span = 10))
    var_vol = var_vol[var_vol.apply(lambda x: abs(x))<10] ### On ne garde que les variations 'normales'
    #'''Pour chaque groupe : variation relative de prix entre l année précédent la chute et l année suivante'''
    var_prix = base_brute.groupby('Id_Groupe').apply(lambda x: prix_chute_brevet(x, average_over = 12, span = 10, selection='ecart_princeps_generique'))
    
    vol = base_brute.groupby('Id_Groupe').apply(lambda x: volume_moyen(x, average_over=12, selection='princeps'))
    prix = base_brute.groupby('Id_Groupe').apply(lambda x: prix_moyen(x, average_over=12, selection='princeps'))
    
    taux_rembours = base_brute.groupby('Id_Groupe')['Taux_rembours'].apply(lambda x: x.iloc[0])
    
    var_vol.name = 'var_vol'
    var_prix.name = 'var_prix'
    vol.name = 'vol'
    prix.name = 'prix'
    taux_rembours.name = 'taux_rembours'
    
    
    '''Visualisation de la distribution des variations de prix'''
    #plt.hist(list(testo[~testo.isnull()]), bins = 20)
    #plt.show()
    
    '''Nombre de labos par princeps'''
    #nb_labos_par_princeps = base_brute.groupby('Id_Groupe').apply(lambda x: plusieurs_labos_par_princeps(x))
    '''Nombre de labos par groupe'''
    #nb_labos_par_groupe = base_brute.groupby('Id_Groupe').apply(lambda x: x['LABO'].nunique())    
    
    '''Voir pour quels groupes la chute du brevet entraine un nouveau groupe dans la même classe par le même labo'''
    #nb_nouveaux_princeps = base_brute.groupby('Id_Groupe').apply(lambda x : nombre_de_nouveaux_princeps(x, sel_labo=False, duree = 20))
    #nb_nouveaux_princeps = base_brute.groupby('Id_Groupe').apply(lambda x : x['C'])
    #code_du_groupe = base_brute.groupby('Id_Groupe').CODE_ATC.apply(lambda x: x.iloc[0])
    #nb_nouveaux_princeps = nb_nouveaux_princeps[nb_nouveaux_princeps != (-1,0)]
    #nb_nouveaux_princeps = nb_nouveaux_princeps[nb_nouveaux_princeps.apply(lambda x: x[0] != 0)]
    
    '''Visualisation : variation de volume en fonction du nombre de labos créant des princeps (par ex)'''
    #test = pd.merge(pd.DataFrame(nb_labos_par_princeps), pd.DataFrame(testo), left_index = True, right_index = True, how='inner')
    #test = pd.merge(test, pd.DataFrame(code_du_groupe), left_index = True, right_index = True, how='inner')
    #plt.scatter(test.iloc[:,0], test.iloc[:,1])
    #plt.show()
    
