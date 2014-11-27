# -*- coding: utf-8 -*-
"""
Created on Thu Nov 27 17:58:30 2014

@author: work
"""

voyelles = ['a', 'e', 'i', 'o', 'u', 'y', ' ']

def compare(reference, *labels):
    for voyelle in voyelles:
        reference = reference.replace(voyelle, '')
    
