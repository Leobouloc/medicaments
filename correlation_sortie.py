# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 18:17:24 2014

@author: work
"""

import numpy as np
import pandas as pd
from pandas import DataFrame
import pdb
import datetime as dt
import matplotlib.pyplot as plt
import scipy.stats as stats

from medic_gouv_with_dosage_strategie2 import load_medic_gouv
from sniiram import load_sniiram

table =load_medic_gouv(maj_bdm,['CIS','Code_Substance', 'Id_Groupe','Prix','indic_droit_rembours','Date_declar_commerc'])
sniiram=load_sniiram()