

def fill_config():
    from baseapp.config import Config
    config = Config()
    # config['truncated_description_len'] = 80
    config['copies_select_size'] = 5                                               # Number of elements to display when listing copies of a book
    config['user_after_registration_groups'] = ['Readers']                         # User joins these groups right after he is registered
    config['default_go_back_link_name'] = 'Go back to searching.'                  # Name of link displayed when filtering books/copies/...
    config['rental_duration'] = 30                                                 # For how long you rent a book
    config['reservation_rush'] = 4                                                 # How quick you need to rent reserved book when it becomes available
    config['default_email_sender'] = 'NSN library <no-reply@library.nsn.wroc.pl'   # From what address user receives emails
    config['message_book_reserved'] = 'Reservation active since %s'                # Message to show right after user reserves a book. Has to contain exactly one %s which will be filled with reservation start date
    config['book_request_info_min_len'] =  10                                      # Minimal length of book request information
    config['list_only_existing_categories_in_search'] = True                       # True iff in booklist (book search, not book copy search) only those categories will be listed, that exists a book with such category.

    return config
