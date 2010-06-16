

def fill_config():
    from baseapp.config import Config
    config = Config()

    # registration
    config['user_after_registration_groups'] = ['Readers']                         # User joins these groups right after he is registered

    # emails
    config['send_emails'] = False                                                  # True iff app will send emails.
    config['log_send_emails'] = True                                               # True iff send emails will be stored in db. Logging doesn't care about send_emails value
    config['default_email_sender'] = 'NSN library <no-reply@library.nsn.wroc.pl>'  # From what address user receives emails

    # reservation/rental
    config['rental_duration'] = 30                                                 # For how long you rent a book
    config['reservation_rush'] = 4                                                 # How quick you need to rent reserved book when it becomes available
    config['message_book_reserved'] = 'Reservation active since %s till %s'        # Message to show right after user reserves a book. Has to contain exactly to %s which will be filled with reservation start and end date

    # book request
    config['book_request_info_min_len'] =  10                                      # Minimal length of book request information

    # searching
    config['copies_location_select_size'] = 5                                      # Number of location elements to display in select list when filtering copies of a book
    config['categories_select_size'] = 6                                           # Number of categories displayed in select list while filtering books
    config['list_only_existing_categories_in_search'] = True                       # True iff in booklist (book search, not book copy search) only those categories will be listed, that exists a book (in database) with such category.
    config['cut_categories_list_to_found_books'] = False                           # True iff in booklist (book search, not book copy search) only those categories will be listed, that exists a book (in results) with such category.

    # misc
    config['is_cost_center_visible_to_anyone'] = True                              # True iff copy's cost center info is visible to anyone (= no perms required)
    config['default_go_back_link_name'] = 'Go back to searching.'                  # Name of link displayed when filtering books/copies/...

    return config
