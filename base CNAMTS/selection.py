# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 13:07:33 2015

@author: Alexis Eidelman
"""



def selection(tab, crit1=None, crit2=None):
    '''renvoie une base qui contient seulement les médicaments qui :
            - sont présents dans au moins crit1 départements
            - ont été vendu au moins crit2 fois
            - ont été vendu au moins crit3 fois dans crit1 départements qui sont les mêmes
    '''


