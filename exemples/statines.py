# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 22:37:37 2014

@author: alexis
"""
import exploitation_sniiram

#import display_and_graphs as dis
#dis.graph_prix_classe('C10AA')
graph_volume_classe(CODE_ATC="C10AA05")

def graph_volume_classe(input_val=None, CODE_ATC=None, Id_Groupe=None, color_by='Id_Groupe',
                        make_sum=False, proportion=False, average_over=12,
                        variations=False, display='cout', write_on=True):