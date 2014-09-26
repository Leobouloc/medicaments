# -*- coding: utf-8 -*-
"""
Created on Wed Sep 24 12:10:10 2014

@author: work
"""

import pandas as pd
import os
from CONFIG import path_BDM_prix
from CONFIG import path_BDM_prix_harmonise

#test.iloc[0].loc[~test.iloc[0,:].isnull()]

#[[i,test.iloc[2].loc[~test.iloc[2,:].isnull()].loc[i]] for i in test.iloc[2].loc[~test.iloc[2,:].isnull()].index]


def load_cnamts_prix_harmonise():
    
    table = pd.read_csv(path_BDM_prix_harmonise + '\\BDM_PRIX_harmonise.csv', sep=',')
    #On rend les colonnes compatibles avec 'period'    
    table.columns = ['CIP']+ ['prix_' + x for x in table.columns[1:]]
    return table

#Creation de la base harmonisée
def load_cnamts_prix():
    '''On obtient pour chaque CIP13 une liste de tuples Date // Prix qui correspond aux dates et changements de prix'''
    table = pd.read_csv(path_BDM_prix + '\\BDM_PRIX.csv', sep=';')
    table['PRIX_E'] = table['PRIX_E'].apply(lambda x: float(x)/100)
    test = table.pivot(index='CIP',columns='DATE_APPLI',values='PRIX_E')
    test.columns = list(pd.Series(test.columns).apply(lambda x: x[6:10] + x[3:5]))
    test = test.groupby(test.columns, axis=1).sum()
    test=test.sort(axis=1) #sort by column value
    
    #138 correspond à la longeur de 'period', nombre de mois dans la base sniiram
    period_sniiram = ['20'+"%02.f"%x+"%02.f"%y for x in range(3,15) for y in range(1,13)][:138]
    output = pd.DataFrame(index=test.index, columns=period_sniiram)
    output[[x for x in period_sniiram if x in list(test.columns)]]=test[[x for x in period_sniiram if x in list(test.columns)]]    

    ## ATTENTION : On enlève manuellement la ligne vide pour un chargement plus rapide
    output = output.loc[output.index!=3400926606053,:]
    # Ici la ligne pour un code réutilisable : output = output.loc[output.apply(lambda x: sum(~x.isnull()),axis=1)!=0,:]
    output.iloc[:,0] = output.apply(lambda x: x[x.first_valid_index()],axis=1)
    output=output.apply(lambda x: remplissage_ligne(x), axis=1)

def remplissage_ligne(ligne):
    assert np.isnan(ligne[0])==False
    for i in range(1,len(ligne)):
        if np.isnan(ligne[i]):
            ligne[i]=ligne[i-1]
    return(ligne)
    #output['CIP']=pd.DataFrame(test.index)
    return output 
    
 

# Pour renvoyer un dictionnaire, utiliser la commande ci dessous   
#output=test.apply(lambda x: [{'Date' : i,'Prix' : x.loc[~x.isnull()].loc[i]} for i in x.loc[~x.isnull()].index],axis=1)    
   
    
    
    
#    table['DATE_APPLI'] = table['DATE_APPLI'].map(lambda t : dt.datetime.strptime(t,"%d/%m/%Y").date())
#    table['date_appli_str'] = float('NaN')
#    for idx in table.index:
#        year = str(table.loc[idx, 'DATE_APPLI'].year)
#        month = str(0) + str(table.loc[idx, 'DATE_APPLI'].month)
#        table.loc[idx, 'date_appli_str'] = float(year + month[-2:])
#    return table