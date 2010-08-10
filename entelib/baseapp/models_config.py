# -*- coding: utf-8 -*-

#TODO: fix ordering of those
'''
Settings for baseapp models. Constants and so on.
'''


emaillog_sender_len = 100             # sender's email (or name and email like: Adny Aloy <andyal@mail.com> )
emaillog_receiver_len = 100           # receiver's email
emaillog_subject_len = 100            # subject of email
emaillog_body_len = 500               # content of email

configuration_key_len = 60
configuration_value_len = 256
configuration_descirption_len = 200

location_name_len = 30
location_remarks_len = 70

building_name_len = 30
building_remarks_len = 50

phone_value_len = 30                  # i.e. len('515-626-737')
phonetype_name_len = 30               # i.e. len('Skype'), len('fax')
phonetype_verify_re_len = 100         # regular expression to verify phone type correctness
phonetype_description_len = 100       # some info for users. One can give example phone numbers

state_name_len = 30
state_description_len = 200           # hover description

publisher_name_len = 50

author_name_len = 50

book_title_len = 50

copy_toc_url_len = 256                # url to table of contents
copy_desc_url_len = 256               # url to site with description
shelf_mark_len = 15

costcenter_name_len = 50              # name of Cost Center

category_name_len = 30                # name of a category
