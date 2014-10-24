# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 11:49:11 2014

@author: work
"""

table_names = ['PDPI_BNFT.csv', 'ADDR_BNFT.csv']

path = 'C:\\Users\\work\\Documents\\ETALAB_data\\UK_medic'

#ACT cost is actual cost
#NIC : Net Ingredient cost

file = os.path.join(path, 'PDPI_BNFT.csv')
#table = pd.read_csv(file)
#table = table.iloc[:,:-1]
table.columns = ['SHA', 'PCT', 'practice', 'BNF_code', 'BNF_name', 'items', 'NIC', 'actual_cost', 'qtt', 'period']

file = os.path.join(path, 'ADDR_BNFT.csv')
table2 = pd.read_csv(file, header = None)
table2.columns = ['date', 'code', 'name', 'address', 'street', 'address_2', 'city', 'post_code']
table2['name'] = table2['name'].apply(lambda x: x.rstrip())