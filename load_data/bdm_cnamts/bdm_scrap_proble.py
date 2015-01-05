# -*- coding: utf-8 -*-
"""
Created on Tue Dec 23 11:51:46 2014

@author: debian
"""
import os

from CONFIG import path_BDM_scrap

from bdm_scrap import cip_from_file_name, parse

if __name__ == '__main__':
#    file_name = r'C:\Users\work\Documents\Etalab_data\AFM\BDM_scrap\cip\3400931713869.html'
#    parse(file_name)
    list_cip = os.listdir(os.path.join(path_BDM_scrap, 'cip'))
    table = None
    i = 0
    problem = []

    ## Probleme
    with open (os.path.join(path_BDM_scrap, 'problem.txt'), "r") as myfile:
        problems = myfile.read().split(';')
        problems_cip = [cip_from_file_name(probl) for probl in problems]
        problems = [os.path.join(path_BDM_scrap, 'cip', probl + '.html') for probl in problems_cip]

    for file in problems:
        i += 1
        if i % 100 == 0:
            print 'on en a fait', i
        file_name = os.path.join(path_BDM_scrap, 'cip', file)
        tab = parse(file_name)
        if table is None:
            table = tab
        else:
            table = table.append(tab)


    ### Taux de remplissage par colonne
    print table.apply(lambda x: x.notnull().sum() / float(len(x)))



