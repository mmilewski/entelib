
def _svd(config, can_override, key, value, desc):
    ''' SVD ~~> set value description. '''
    config[key] = value
    config.set_description(key, desc)
    config.set_can_override(key, can_override)


def fill_config():
    from baseapp.config import Config
    config = Config()
    config.clear(truncate_config=True)

    # registration
    _svd(config, False, 'user_after_registration_groups', ['Readers'],                  "User joins these groups right after he is registered")

    # emails
    _svd(config, False, 'send_emails',           False,                                       "True iff app will send emails.")
    _svd(config, False, 'log_send_emails',       True,                                        "True iff send emails will be stored in db. Logging doesn't care about send_emails value")
    _svd(config, False, 'default_email_sender', 'NSN library <no-reply@library.nsn.wroc.pl>', "From what address user receives emails")
    _svd(config, False, 'default_email_subject', 'NSN library notification',                  "With what subjects user receives emails")

    # reservation/rental
    _svd(config, False, 'rental_duration',        30,                                   "For how long you rent a book")
    _svd(config, False, 'reservation_duration',   30,                                   "For how long you can reserve a book")
    _svd(config, False, 'reservation_rush',       4,                                    "How quick you need to rent reserved book when it becomes available")
    _svd(config, False, 'message_book_reserved', 'Reservation active since %s till %s', "Message to show right after user reserves a book. Has to contain exactly two `%s` which will be filled with reservation start and end date")
    _svd(config, False, 'message_book_rented',   'Rental made untill %s.',              "Message to show right after user rents a book. Has to contain exactly one `%s` which will be filled with rental end date")

    # book request
    _svd(config, False, 'book_request_info_min_len', 10,                                "Minimal length of book request information")
    _svd(config, False, 'book_request_info_template', 'Title:\n\n\nAuthors:\n\n\nPublication:\n\n\nUrl:\n\n',   "Template which is displayed to help in filling request book form")

    # searching
    _svd(config, True , 'copies_location_select_size',              5,                  "Number of location elements to display in select list when filtering copies of a book")
    _svd(config, True , 'categories_select_size',                   6,                  "Number of categories displayed in select list while filtering books")
    _svd(config, True , 'list_only_existing_categories_in_search',  True,               "True iff in booklist (book search, not book copy search) only those categories will be listed, that exist a book (in database) with such category.")
    _svd(config, True , 'cut_categories_list_to_found_books',       False,              "True iff in booklist (book search, not book copy search) only those categories will be listed, that exist a book (in results) with such category.")
    _svd(config, False, 'when_reserved_period',                     90,                 "When listing book copies, it says for how many days forward user will be shown when a copy is reserved.")
    _svd(config, True , 'enable_time_bar',                          True,               "True iff time bar will be displayed.")

    # time bar
    _svd(config, False, 'tb_max_days_in_date_range',                365,                "Time bar. Max number of days date range can describe. If wider then the range will be shortened.")
    _svd(config, False, 'tb_max_days_to_display_days',               10,                "Time bar. Max number of days in date range, for which scale unit will be one day.")
    _svd(config, False, 'tb_max_days_to_display_weeks',              40,                "Time bar. Max number of days in date range, for which scale unit will be one week (or one day, see tb_max_days_to_display_days).")

    # misc
    _svd(config, False, 'is_cost_center_visible_to_anyone',     False,                    "True iff copy's cost center info is visible to anyone (= no perms required)")
    _svd(config, False, 'default_go_back_link_name',            'Go back to searching.', "Name of link displayed when filtering books/copies/...")
    _svd(config, True , 'display_tips',                         False,                   "True iff tips are visible")
    _svd(config, False, 'display_only_editable_config_options', True,                   "True iff user see only editable options.")
    return config
