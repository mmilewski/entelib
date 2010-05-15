# -*- coding=utf-8 -*-

#TODO: wymyślić jakiś sensowny sposób ułożenia tych zmiennych. Chyba że po prostu każdą wartość będziemy definiować pod istniejącymi. Co chyba nie jest rzadkim rozwiążązaniem...
'''
Settings for baseapp models. Constants and so on.
'''

configuration_key_len = 20
configuration_value_len = 256

location_name_len = 30
location_remarks_len = 50

phone_value_len = 30                  # i.e. len('515-626-737')
phonetype_name_len = 30
phonetype_verify_re_len = 100         # regular expression to verify phone type correctness
phonetype_description_len = 100       # some info for users. One can give example phone numbers

state_name_len = 30

publisher_name_len = 50

picture_description_len = 50
picture_upload_to = 'book_pictures'      # directory where pictures will be uploaded

author_name_len = 50

book_title_len = 50

copy_toc_url_len = 256                # url to table of contents

costcenter_name_len = 50              # name of Cost Center

category_name_len = 30                # name of a category
