

def _svd(config, key, value, desc):
    ''' SVD ~~> set value description. '''
    config[key] = value
    config.set_description(key, desc)


def fill_config():
    from baseapp.config import Config
    config = Config()
    config.clear(truncate_model=True)

    # registration
    # config['user_after_registration_groups'] = ['Readers']                         # User joins these groups right after he is registered
    _svd(config, 'user_after_registration_groups', ['Readers'],                  "User joins these groups right after he is registered")

    # emails
    # config['send_emails'] = False                                                  # True iff app will send emails.
    # config['log_send_emails'] = True                                               # True iff send emails will be stored in db. Logging doesn't care about send_emails value
    # config['default_email_sender'] = 'NSN library <no-reply@library.nsn.wroc.pl>'  # From what address user receives emails
    _svd(config, 'send_emails',           False,                                       "True iff app will send emails.")
    _svd(config, 'log_send_emails',       True,                                        "True iff send emails will be stored in db. Logging doesn't care about send_emails value")
    _svd(config, 'default_email_sender', 'NSN library <no-reply@library.nsn.wroc.pl>', "From what address user receives emails")

    # reservation/rental
    # config['rental_duration'] = 30                                                 # For how long you rent a book
    # config['reservation_rush'] = 4                                                 # How quick you need to rent reserved book when it becomes available
    # config['message_book_reserved'] = 'Reservation active since %s till %s'        # Message to show right after user reserves a book. Has to contain exactly to %s which will be filled with reservation start and end date
    _svd(config, 'rental_duration',        30,                                   "For how long you rent a book")
    _svd(config, 'reservation_rush',       4,                                    "How quick you need to rent reserved book when it becomes available")
    _svd(config, 'message_book_reserved', 'Reservation active since %s till %s', "Message to show right after user reserves a book. Has to contain exactly to %s which will be filled with reservation start and end date")

    # book request
    # config['book_request_info_min_len'] =  10                                      # Minimal length of book request information
    _svd(config, 'book_request_info_min_len', 10,                                "Minimal length of book request information")

    # searching
    # config['copies_location_select_size'] = 5                                      # Number of location elements to display in select list when filtering copies of a book
    # config['categories_select_size'] = 6                                           # Number of categories displayed in select list while filtering books
    # config['list_only_existing_categories_in_search'] = True                       # True iff in booklist (book search, not book copy search) only those categories will be listed, that exists a book (in database) with such category.
    # config['cut_categories_list_to_found_books'] = False                           # True iff in booklist (book search, not book copy search) only those categories will be listed, that exists a book (in results) with such category.
    _svd(config, 'copies_location_select_size',              5,                  "Number of location elements to display in select list when filtering copies of a book")
    _svd(config, 'categories_select_size',                   6,                  "Number of categories displayed in select list while filtering books")
    _svd(config, 'list_only_existing_categories_in_search',  True,               "True iff in booklist (book search, not book copy search) only those categories will be listed, that exists a book (in database) with such category.")
    _svd(config, 'cut_categories_list_to_found_books',       False,              "True iff in booklist (book search, not book copy search) only those categories will be listed, that exists a book (in results) with such category.")
    _svd(config, 'when_reserved_period',                     90,                 "When listing book copies, it says for how many days forward user will be shown when a copy is reserved.")
    _svd(config, 'enable_time_bar',                          True,               "Choose between table sorting and time bars showing in book copies view.")

    # misc
    # config['is_cost_center_visible_to_anyone'] = True                              # True iff copy's cost center info is visible to anyone (= no perms required)
    # config['default_go_back_link_name'] = 'Go back to searching.'                  # Name of link displayed when filtering books/copies/...
    _svd(config, 'is_cost_center_visible_to_anyone',    True,                    "True iff copy's cost center info is visible to anyone (= no perms required)")
    _svd(config, 'default_go_back_link_name',           'Go back to searching.', "Name of link displayed when filtering books/copies/...")

    return config
