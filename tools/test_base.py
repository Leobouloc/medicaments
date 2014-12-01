# -*- coding: utf-8 -*-
"""
Created on Fri Nov 28 10:49:20 2014

@author: work
"""

'''########### - TEST Volume 1 - #############'''
'''Vérifie si les ventes en nb de boites sont bien nan ou entiers'''
print 'TEST Volume 1 : Comptage des ventes de boites décimales'

def check_lambda(x):
    
    if np.isnan(x):
        return True
    elif x.is_integer():
        return True
    else:
        return False

a = base_brute[period].applymap(check)
nb_non_entiers = (~a).sum().sum() # = 0 // Pas de décimaux (c'est bien)
print 'On a ' + str(nb_non_entiers) + ' ventes de boites décimales'

'''########### - TEST Volume 2 - #############'''
'''Vérifie si les ventes en nb de boites sont bien positives'''
print 'TEST Volume 2 : Comptage des ventes de boites négatives'

a = base_brute[period] < 0
print 'On a ' + str(a.sum().sum()) + ' ventes de boites négatives'

'''########### - TEST Prix 1 - #############'''
'''Vérifie si les ventes en nb de boites sont bien positives'''
print 'TEST Prix 1 : Comptage prix des boites négatifs'

a = base_brute[period_prix] <= 0
print 'On a ' + str(a.sum().sum()) + ' prix de boites négatifs'