# -*- coding: utf-8 -*-
"""
Created on Thu Oct 02 10:12:13 2014

@author: work
"""

import matplotlib

colors = [hex for name, hex in matplotlib.colors.cnames.iteritems()]
colors.remove('#FFE4E1')
#colors =['#002b36', '#073642', '#586e75', '#657b83', '#839496', '#93a1a1', '#eee8d5',
        # '#fdf6e3','#b58900','#cb4b16','#dc322f','#d33682','#6c71c4','#268bd2','#2aa198','#859900']


#Montre le nombre de groupes par code substance substance


def class_count(niveau=4):
    if niveau == 4:
        string = 'CODE_ATC_4'
    elif niveau == 6:
        string = 'CODE_ATC'
    for code in set(base_brute[string]):
        b = set(base_brute.loc[base_brute[string] == code, 'Id_Groupe'])
        print str(code) + ' --->> ' + str(len(b))
        print b

def select(table):
    ''' Permet d'appliquer les conditions (ci dessus) à la table '''
    table2 = table.loc[cond.index[cond]]
    return table2


def print_role(data, Type=False):
    '''Sert dans info_display'''
    if Type:
        assert 'Type' in data.columns
        role = data['Type']
#        assert any(role == 0) # Il y a nécéssairement un princeps
        print ('\n *** princeps ***' )
        print (data[role == 0])
        if any(role == 1):
            print ('\n *** génériques ***' )
            print (data[role == 1])
        else:
            print ('\n pas de générique pour ce groupe' )
    else:
        print data


def info_display(data, input_val=None , name=None ,CIP13=None, Id_Groupe=None, CODE_ATC=None, variables=None, return_tab=False):
    '''Display des informations sur les medicaments,
        choisir les données à montrer dans "variables",
        return_tab=True si on veut renvoyer un objet, =False pour le print'''

    ###############################################################################
    ########### Début : Remplissage automatique des variables

    # On choisit par défaut l'ATC de niveau 4 pour le display
    string_atc = 'CODE_ATC_4'

    # Si on entre un ATC complet, on display l'ATC complet
    if (CODE_ATC is not None) and len(CODE_ATC) == 7:
        string_atc = 'CODE_ATC'

    #Détecte si l'input correspond au groupe, à la classe (4 ou 5) ou au CIP13
    if input_val is not None:
        if isinstance(input_val, str):
            if len(input_val) == 13:
                CIP13 = input_val
            elif len(input_val) == 5:
                CODE_ATC = input_val
            elif len(input_val) == 7:
                CODE_ATC = input_val
                string_atc = 'CODE_ATC'
            else:
                print 'input_val is unidentified string'
        elif isinstance(input_val, int):
            Id_Groupe = input_val
        else:
            print 'input val is unidentified'

    ########### Fin : Remplissage automatique des variables
    ###############################################################################

    if variables is None:
        vars_display=['Id_Groupe', 'Type', 'LABO', 'Date_declar_commerc',
                      'prix_par_dj_201401']
    else:
        vars_display = variables
    if name is not None:
        disp = data.loc[data['Nom'].str.contains(name, case=False, na=False), vars_display]
    if CIP13 is not None:
        disp = data.loc[data['CIP13'] == CIP13, vars_display]
    if CODE_ATC is not None:
        disp = data.loc[data[string_atc] == CODE_ATC, vars_display]
    if Id_Groupe is not None:
        disp = data.loc[data['Id_Groupe'] == Id_Groupe, vars_display]

    if return_tab:
        return disp
    else:
        Type = 'Type' in vars_display
        if 'Id_Groupe' in vars_display:
            for grp in list(set(disp['Id_Groupe'])):
                print_role(disp.loc[disp['Id_Groupe'] == grp, :], Type)
                print '\n'
        else:
            print_role(disp, Type)
    #return disp

def moving_average(table, size=12):
    if size == 0:
        return table
    else:
        assert size % 2 == 0
        mid_size = size/2
        output = pd.DataFrame(columns=table.columns, index=table.index)
        for date in range(mid_size, len(table.columns) - mid_size):
            output[output.columns[date]] = table.iloc[:, (date-mid_size+1):(date+mid_size+1)].mean(axis=1)  # les dépenses du mois sont prise en fin de mois
    #     for group in output.index:
    #         output[table[table.index == group].isnull()] = None
        return output


def evolution(table):
    '''Calcul des differences de consommation'''
    evolution = pd.DataFrame(index=table.index, columns=period[1:])
#    table[table == 0] = None
    last_month = table[period[0]]
    for month in period[1:]:
        evolution[month] = (table[month] - last_month)  # /last_month
        last_month = table[month]
    return evolution


def graph(group):
    ''' Créer le plot de comparaison entref princeps et generic '''
    plt.close()
    col0 = nombre_princeps[nombre_princeps.index == group].values
    col1 = nombre_generic[nombre_generic.index == group].values
    col2 = col0 + col1
    output = DataFrame({'princeps': col0, 'generic': col1, 'total': col2}, index=period_str).plot()
    plt.show()


def graph_ma(group):
    ''' Créer le plot de comparaison entre princeps et generic '''
    plt.close()
    col0 = moving_average_princeps[moving_average_princeps.index == group]
    col1 = moving_average_generic[moving_average_generic.index == group]
    col2 = col0.add(col1, fill_value=0)
    col0 = col0.values
    col1 = col1.values
    col2 = col2.values

    if len(col1) > 0:  # On vérifie que col1 n'est pas vide (i.e. qu'il y a des génériques)
        output = DataFrame({'ma_princeps': col0[0], 'ma_generic': col1[0], 'ma_total': col2[0]}, index=period_str)
    else:
        output = DataFrame({'ma_princeps': col0[0], 'ma_total': col2[0]}, index=period_str)
    #print output
    output.plot()
    plt.show()


def graph_prix_classe(input_val=None, CODE_ATC=None, Id_Groupe=None, color_by='Id_Groupe', average=False, string_atc='CODE_ATC_4'):
    '''Crée le plot du prix par substance pour tous les médicaments d'une même classe ATC'''

    ###############################################################################
    ########### Début : Remplissage automatique des variables

    # On choisit par défaut l'ATC de niveau 4 pour le display

    if input_val is not None:
        if isinstance(input_val, str):
            if len(input_val) == 5:
                CODE_ATC = input_val
            elif len(input_val) == 7:
                CODE_ATC = input_val
                string_atc = 'CODE_ATC'
            else:
                print 'input_val is unidentified string'
        elif isinstance(input_val, int):
            Id_Groupe = input_val
        else:
            print 'input val is unidentified'

    # Si on entre un ATC complet, on display l'ATC complet
    if CODE_ATC is not None and len(CODE_ATC) == 7:
        string_atc = 'CODE_ATC'

    #Si on rentre un groupe, on détermine le code ATC associé
    if Id_Groupe is not None:
        CODE_ATC = base_brute.loc[base_brute['Id_Groupe'] == Id_Groupe, string_atc].iloc[0]
        print CODE_ATC
        if not isinstance(CODE_ATC, unicode):
            print 'CODE_ATC_4 inconnu'

    ########### Fin : Remplissage automatique des variables
    ###############################################################################

    plt.close()
    assert sorted(period) == period
    assert sorted(period_prix) == period_prix

    i = 0
    select = base_brute.loc[:, string_atc] == CODE_ATC
    #base_brute = base_brute.apply(lambda x: rewrite period_prix(x), axis = 1)
    for value in set(base_brute.loc[select, color_by]):
        output = base_brute[select].loc[base_brute.loc[select, color_by] == value, period_prix_par_dj]
        output.index = base_brute[select].loc[base_brute.loc[select, color_by] == value, 'CIP13']
        # output.columns = [12*(int(x)/100-2003 + period] # Façon la plus simple d'avoir une axe des abcisses qui montre la date
        if average:
            output = output.mean()
            plt.plot(output.transpose(), color=colors[i], label=str(value))
        else:
            plt.plot(output.transpose(), color=colors[i])

        if color_by == 'Id_Groupe':
            date_generique = int(date_generication_groupe.loc[value])
            x = 'prix_par_dj_' + str(date_generique)
            if average:
                ymax = output[x]
            else:
                ymax = max(output[x])
            print ymax
            x = get_index(date_generique)
            plt.vlines(x, 0, ymax, color=colors[i], linestyles='--')

        i = i+1
    plt.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=1)
    plt.show()


def graph_volume_classe(input_val=None, CODE_ATC=None, Id_Groupe=None, color_by='Id_Groupe',
                        make_sum=False, proportion=False, average_over=12,
                        variations=False, display='cout', write_on=True):
    '''Le cout est le produit du dosage vendu et du prix par dosage'''
    '''color_by choisit le champ déterminant pour la couleur'''
    '''make_sum détermine si l'on somme suivant le critère défini par color_by'''
    '''proportion permet d'afficher la proportion de chaque sélection par rapport à la somme totale'''
    '''average over détermine l'amplitude choisie pour le lissage (0 : pas de lissage)'''
    '''variations = True permet d'afficher les variation'''

    assert display in ['cout', 'volume']

    ###############################################################################
    ########### Début : Remplissage automatique des variables

    # On choisit par défaut l'ATC de niveau 4 pour le display
    string_atc = 'CODE_ATC'

    if input_val != None:
        if isinstance(input_val, str):
            if len(input_val) == 5:
                CODE_ATC = input_val
                string_atc = 'CODE_ATC_4'
            elif len(input_val) == 7:
                CODE_ATC = input_val
                string_atc = 'CODE_ATC'
            else:
                print 'input_val is unidentified string'
        elif isinstance(input_val, int):
            Id_Groupe = input_val
        else:
            print 'input val is unidentified'

    # Si on entre un ATC complet, on display l'ATC complet
    if CODE_ATC is not None and len(CODE_ATC) == 7:
        string_atc = 'CODE_ATC'

    #Si on rentre un groupe, on détermine le code ATC niv 4 associé
    if Id_Groupe is not None:
        CODE_ATC = base_brute.loc[base_brute['Id_Groupe'] == Id_Groupe, string_atc].iloc[0]
        if not isinstance(CODE_ATC, unicode):
            print 'CODE_ATC_4 inconnu'

    ########### Fin : Remplissage automatique des variables
    ###############################################################################
    ########### Début : Selection des données à visualiser

    plt.close()
    assert sorted(period) == period
    assert sorted(period_prix) == period_prix
    i = 0 # Sert pour le choix de la couleur

    select = base_brute.loc[:, string_atc] == CODE_ATC

    # Choix du type de display (cout total ou dosage remboursé)
    if display == 'cout':
        tab1 = base_brute.loc[select, period_nb_dj_rembourse]
        tab2 = base_brute.loc[select, period_prix_par_dj]
        #Faire la moyenne
        tab1.columns = period
        tab2.columns = period
        output = tab1 * tab2
    elif display == 'volume':
        output = base_brute.loc[select, period_nb_dj_rembourse]

    if variations:
        output = evolution(output)
    output = moving_average(output, average_over)

    # Sert pour le calcul des proportions et visualisation du Total sur classe
    sum_output = output.sum(axis=0, skipna=True)

    ########### Fin : Selection des données à visualiser
    ###############################################################################
    ########### Début : Visualisation

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Pour toutes les valeurs à differencier (ex : value peut prendre 192 (Id du groupe))
    for value in set(base_brute.loc[base_brute.loc[:, string_atc]==CODE_ATC, color_by]):

        output_group = output.loc[base_brute.loc[select, color_by] == value]

        if proportion:
            output_group = output_group.div(sum_output)
        if make_sum:
            output_group = output_group.sum(skipna = True)
        else:
            output_group.columns = range(len(output_group.columns))
        output_group.index = range(len(output_group.index))
        ###########################################################################
        ####### Début : Visualisation/ Somme sur les groupes
        if make_sum:
            ax.plot(output_group.transpose(), color = colors[i], label = str(value))
            if color_by == 'Id_Groupe':
                date_generique = date_generication_groupe.loc[value]
                x = get_index(date_generique)
                ymax = output_group[x]
                ax.vlines(x,0, ymax, color = colors[i], linestyles = '--')
                if write_on and color_by == 'Id_Groupe':
                    princeps = base_brute[base_brute.apply(lambda x: x['Id_Groupe']==value and x['Type'] == 0, axis = 1)]
                    if len(princeps) != 0:
                        index = princeps['premiere_vente'].argmin()
                        princeps = princeps.loc[index]
                        x = princeps['premiere_vente']
                        #print(output_group.index)
                        x = get_index(x)
                        if x < average_over/2:
                            x = average_over/2
                        elif (len(period) - x) < average_over/2:
                            x = len(period) - average_over/2
                        y = output_group[x]
                        info_str = str(princeps['LABO']) + ' / ASMR : ' + str(princeps['Valeur_ASMR'])

                        print (x, y)
                        if not np.isnan(y):
                            ax.annotate(info_str, xytext=(x,y), color = colors[i], xy=(0,0), annotation_clip = False)
                            x = princeps['premiere_vente']
                            x = get_index(x)
                            y = output_group[x]
                            ax.scatter(x,y, marker = 'o', color = colors[i], s = 100)
        ####### Fin : Visualisation/ Somme sur les groupes
        ###########################################################################
        ####### Début : Visualisation/ Pas de somme sur les groupes
        else:
            for j in output_group.index:

                #Mise en place de la légende
                if write_on:
                    a = base_brute.loc[select]
                    b = a.loc[base_brute.loc[select, color_by] == value]
                    label = b['Nom'].iloc[j][:15]#On tronque pour garder 15 charactères
                    ax.plot(output_group.loc[j,:], color = colors[i])
                    x = get_index(b['premiere_vente'].iloc[j])
                    if x < average_over/2:
                        x = average_over/2
                    a = float(output_group.loc[j, x])
                    print type (a)
                    if np.isnan(a):
                        a = -1
                    xytext = (x, a)
                #print type(output_group.loc[j, x+6])

                ax.annotate(str(label), xytext=xytext, xy=(0,0), color = colors[i], annotation_clip=False)
                print xytext
        ####### Fin : Visualisation/ Pas de somme sur les groupes
        ###########################################################################

        print i # i sert pour le choix de la couleur
        i = i + 1
    if proportion == False and variations == False:
        plt.plot(sum_output, color = 'k', linestyle = '-', linewidth = 2.0, label = 'Total Classe')
    plt.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=1)
    ax.set_xticklabels([str(period[i]) for i in range(0, len(period)) if i%12 == 0])
    ax.set_xticks([i for i in range(0, len(period)) if i%12 == 0])
    plt.show()
    ########### Fin : Visualisation
    ###############################################################################