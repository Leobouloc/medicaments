# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 16:17:44 2014

@author: User
"""


import cookielib
import urllib2
import os

import pandas as pd

from CONFIG import path_BDM_scrap
url_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))

pas_de_valeur = []
def load_cip(cip, ext):
    global pas_de_valeur
    assert ext in ['avis', 'cip']

    #headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2248.0 Safari/537.36",}
    url = 'http://www.codage.ext.cnamts.fr/codif/bdm//fiche/index_fic_sp_' + ext + '.php?p_code_cip=' + str(cip) + \
     '&p_menu=FICHE&p_site='

    print url
    request = urllib2.Request(url)
    response = url_opener.open(request)
    html_page =  response.read()
    #with io.open('D:\data\Medicament\BDM' + str(cip), 'w') as json_file:
    #    json.dump(html_page, json_file, ensure_ascii=False)

    with open(os.path.join(path_BDM_scrap, ext, str(cip) + '.html'), 'w') as f:
        f.write(html_page)



if __name__ == '__main__':

    ## liste chargé sur le site de BDM
    list_cip0 = []
    for list_num in range(530, 535):
        num = str(list_num)
        tab = pd.read_csv(os.path.join(path_BDM_scrap, 'Fic_liste_CIP' + num + '.xls'), delimiter = '\t')
        cip_table = tab.iloc[:, 0].tolist()
        list_cip0 += cip_table

    print len(list_cip0)
    list_cip0 = set(list_cip0)
    print len(list(list_cip0))

    #  liste présente dans le sniiram
    from load_data.sniiram import load_sniiram
    sniiram = load_sniiram()
    list_cip1 = sniiram.index.tolist()

    print len(list_cip1)
    list_cip1 = set(list_cip1)
    print len(list(list_cip1))

    #  liste présente dans medic_gouv
    from load_data.medic_gouv import load_medic_gouv
    gouv = load_medic_gouv(var_to_keep = ['CIP'])
    list_cip2 = gouv['CIP'].tolist()

    print len(list_cip2)
    list_cip2 = set(list_cip2)
    print len(list(list_cip2))


    manquant_dans_bdm = list_cip1 - list_cip0
    print 'manquant ', len(manquant_dans_bdm)

    manquant_de_gouv_dans_bdm = list_cip2 - list_cip0
    print 'manquant ', len(manquant_de_gouv_dans_bdm)

    # Deja calculé :
    deja_calc = set([cip[:-5] for cip in os.listdir(path_BDM_scrap + 'cip')])
    print len(deja_calc)
    print len((list_cip1 & list_cip0) - deja_calc)
    #for k in range(20):
    #    time.sleep(120)
    #    deja_calc = set([cip[:-5] for cip in os.listdir(path_BDM_scrap + 'cip')])
    #    print len(deja_calc)

    for cip in (list_cip1 & list_cip0) - deja_calc:
        load_cip(cip, 'avis')
        load_cip(cip, 'cip')


    path = 'D:\data\Medicament\BDM\\pas_dans_gouv\\'
    for cip in list_cip0 - list_cip1:
        load_cip(cip, 'avis')
        load_cip(cip, 'cip')
