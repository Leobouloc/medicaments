# -*- coding: utf-8 -*-
"""
Created on Thu Oct 02 10:12:13 2014

@author: work
"""

def select(table):
    ''' Permet d'appliquer les conditions (ci dessus) à la table '''
    table2 = table.loc[cond.index[cond]]
    return table2

def print_role(data, Type=False):
    if Type:
        assert 'Type' in data.columns
        role = data['Type']
        assert any(role == 0) # Il y a nécéssairement un princeps
        print('\n *** princeps ***' )
        print (data[role == 0])
        if any(role == 1):
            print('\n *** génériques ***' )
            print (data[role == 1])
        else:       
            print('\n pas de générique pour ce groupe' )
    else:
        print data
    

def info_display(data, name=None ,CIP13=None, Id_Groupe=None, CODE_ATC= None, variables=None, return_tab=False):
    '''Display des informations sur les medicaments,
        choisir les données à montrer dans "variables",
        return_tab=True si on veut renvoyer un objet, =False pour le print'''
    data.sort(['Id_Groupe', 'premiere_vente'])
    if variables==None:
        vars_display=['Id_Groupe','Type','LABO','Date_declar_commerc','prix_par_dosage_201401']
    else :
        vars_display=variables
    if name != None:
        disp = data.loc[base_brute['Nom'].str.contains(name, case=False, na=False),vars_display]
    if CIP13 != None:
        disp = data.loc[base_brute['CIP13']==CIP13,vars_display]
    if CODE_ATC != None:
        disp = data.loc[base_brute['CODE_ATC']==CODE_ATC,vars_display]
    if Id_Groupe != None:
        disp = data.loc[base_brute['Id_Groupe']==Id_Groupe,vars_display]

    if return_tab:
        return disp
    else:
        Type = 'Type' in vars_display
        if 'Id_Groupe' in vars_display:
            for grp in list(set(disp['Id_Groupe'])):
                print_role(disp.loc[disp['Id_Groupe']==grp,:], Type)
                print '\n'
        else: 
            print_role(disp, Type)
    #return disp

def moving_average(table, size):
    assert size % 2 == 0
    mid_size = size/2
    output = pd.DataFrame(columns=table.columns, index=table.index)
    for date in range(mid_size, len(table.columns) - mid_size):
        output[output.columns[date]] = table.iloc[:,(date-mid_size+1):(date+mid_size+1)].mean(axis=1) #les dépenses du mois sont prise en fin de mois
#     for group in output.index:
#         output[table[table.index == group].isnull()] = None
    return output


def evolution(table):
    '''Calcul des differences de consommation'''
    evolution = pd.DataFrame(index = table.index, columns = period[1:])
    table[table==0] = None
    last_month = table[period[0]]
    for month in period[1:]:
        evolution[month] = (table[month] - last_month)/last_month
        last_month = table[month]
    return evolution


def graph(group):    
    ''' Créer le plot de comparaison entref princeps et generic '''
    plt.close()
    col0 = nombre_princeps[nombre_princeps.index == group].values
    col1 = nombre_generic[nombre_generic.index == group].values
    col2 = col0 + col1
    output = DataFrame({'princeps':col0, 'generic':col1, 'total':col2}, index = period_str).plot()
    plt.show()

def graph_ma(group):
    ''' Créer le plot de comparaison entre princeps et generic '''
    plt.close()
    col0 = moving_average_princeps[moving_average_princeps.index == group]
    col1 = moving_average_generic[moving_average_generic.index == group]
    col2 = col0.add(col1,fill_value=0)
    col0 = col0.values
    col1 = col1.values
    col2 = col2.values

    if len(col1)>0: # On vérifie que col1 n'est pas vide (i.e. qu'il y a des génériques)
        output = DataFrame({'ma_princeps':col0[0], 'ma_generic':col1[0], 'ma_total':col2[0]}, index = period_str)
    else:
        output = DataFrame({'ma_princeps':col0[0], 'ma_total':col2[0]}, index = period_str)
    #print output
    output.plot()
    plt.show()


def graph_ma_classe(CODE_ATC, proportion=False):  # code_substance):
    ''' Créer le plot de comparaison de consommation totale des groupes par classe'''
    plt.close()    
    output = None
    for group in list(set(base_brute.loc[base_brute['CODE_ATC']==CODE_ATC,'Id_Groupe'])):
        print group
        col0 = moving_average_princeps[moving_average_princeps.index == group]
        col1 = moving_average_generic[moving_average_generic.index == group]
        col2 = col0.add(col1,fill_value=0)
        #col2 = col2 / col2.T.mean(skipna=True).values[0]
        col2 = col2.values
        
        if output is None:
            print 'there'
            output=DataFrame(col2[0],index = period_str) #49632
        else :
            try:
                colu=pd.DataFrame(col2[0],index = period_str)
                output = output.join(colu, rsuffix='_'+str(group),how='outer')
            except:
                print 'exception'
    #print output
    if proportion == True:
        output = output.div(output.sum(axis=1), axis=0) #pour avoir la proportion de chaque groupe
    output.plot()
    plt.show()

def graph_prix_classe(CODE_ATC):
    '''Crée le plot du prix par substance pour tous les médicaments d'une même classe ATC'''
    plt.close()
    assert sorted(period)==period
    assert sorted(period_prix)==period_prix
    
    #base_brute = base_brute.apply(lambda x: rewrite period_prix(x), axis = 1)
    
    output = base_brute.loc[base_brute.loc[:,'CODE_ATC']==CODE_ATC, period_prix_par_dosage]
    output.index = base_brute.loc[base_brute.loc[:,'CODE_ATC']==CODE_ATC, 'CIP13']
    #output.columns = [12*(int(x)/100-2003 + period] # Façon la plus simple d'avoir une axe des abcisses qui montre la date
    output.transpose().plot(marker='o')
    plt.show()