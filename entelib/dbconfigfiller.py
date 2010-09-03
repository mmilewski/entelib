from baseapp.models import ConfigurationValueType

def _svd(config, type, can_override, key, value, desc):
    ''' SVD ~~> set value description. '''
    config.insert_or_update_global(key, value, type=type, description=desc, can_override=can_override)
    # config[key] = value
    # config.set_type(key, type)
    # config.set_description(key, desc)
    # config.set_can_override(key, can_override)


def fill_types():
    # print 'filling configuration value types'
    add_one = lambda name: (ConfigurationValueType(name=name).save())
    add_one('int')
    add_one('bool')
    add_one('unicode')
    add_one('list_groupnames')
    # add_one('list_any')
    # add_one('list_str')
    # add_one('list_int')
    # add_one('list_bool')


def fill_config():
    from baseapp.config import Config
    config = Config()
    config.clear(truncate_config=True)
    fill_types()
    
    t_int       = ConfigurationValueType.objects.get(name='int')
    t_bool      = ConfigurationValueType.objects.get(name='bool')
    t_unicode   = ConfigurationValueType.objects.get(name='unicode')
    t_list_groupnames= ConfigurationValueType.objects.get(name='list_groupnames')
    # t_list_any  = ConfigurationValueType.objects.get(name='list_any')
    # t_list_str  = ConfigurationValueType.objects.get(name='list_str')
    # t_list_int  = ConfigurationValueType.objects.get(name='list_int')
    # t_list_bool = ConfigurationValueType.objects.get(name='list_bool')

    # registration
    _svd(config, t_list_groupnames, False, 'user_after_registration_groups', ['Readers'],      "User joins these groups right after he is registered")

    # emails
    _svd(config, t_bool, False, 'send_emails',                            False,                           "True iff app will send emails.")
    _svd(config, t_bool, False, 'log_send_emails',                         True,                           "True iff send emails will be stored in db. Logging doesn't care about send_emails value")
    _svd(config, t_unicode, False, 'default_email_sender',  u'NSN library <no-reply@library.nsn.wroc.pl>', "From what address user receives emails")
    _svd(config, t_unicode, False, 'default_email_subject', u'NSN library notification',                   "With what subjects user receives emails")

    # reservation/rental
    _svd(config, t_int, False, 'rental_duration',                            30,                       "For how long you rent a book")
    _svd(config, t_int, False, 'reservation_duration',                       30,                       "For how long you can reserve a book")
    _svd(config, t_int, False, 'reservation_rush',                            4,                       "How quick you need to rent reserved book when it becomes available")
    _svd(config, t_unicode, False, 'message_book_reserved',  u'Reservation active since %s till %s',   "Message to show right after user reserves a book. Has to contain exactly two `%s` which will be filled with reservation start and end date")
    _svd(config, t_unicode, False, 'message_book_rented',    u'Rental made untill %s.',                "Message to show right after user rents a book. Has to contain exactly one `%s` which will be filled with rental end date")

    # book request
    _svd(config, t_int, False, 'book_request_info_min_len',                  10,                       "Minimal length of book request information")
    _svd(config, t_unicode, False, 'book_request_info_template', u'Title:\n\n\nAuthors:\n\n\nSuggested location:\n\n\nAdditional info:\n\n',   "Template which is displayed to help in filling request book form")

    # searching
    _svd(config, t_int,  True , 'copies_location_select_size',                5,        "Number of location elements to display in select list when filtering copies of a book")
    _svd(config, t_int,  True , 'categories_select_size',                     6,        "Number of categories displayed in select list while filtering books")
    _svd(config, t_bool, True , 'list_only_existing_categories_in_search', True,        "True iff in booklist (book search, not book copy search) only those categories will be listed, that exist a book (in database) with such category.")
    _svd(config, t_bool, True , 'cut_categories_list_to_found_books',     False,        "True iff in booklist (book search, not book copy search) only those categories will be listed, that exist a book (in results) with such category.")
    _svd(config, t_int,  False, 'when_reserved_period',                      90,        "When listing book copies, it says for how many days forward user will be shown when a copy is reserved.")

    # time bar
    _svd(config, t_bool, False, 'enable_time_bar',                         True,        "True iff time bar is displayed.")
    _svd(config, t_int,  False, 'tb_max_days_in_date_range',                365,        "Time bar. Max number of days date range can describe. If wider then the range will be shortened.")
    _svd(config, t_int,  False, 'tb_max_days_to_display_days',               10,        "Time bar. Max number of days in date range, for which scale unit will be one day.")
    _svd(config, t_int,  False, 'tb_max_days_to_display_weeks',              40,        "Time bar. Max number of days in date range, for which scale unit will be one week (or one day, see tb_max_days_to_display_days).")

    # global
    _svd(config, t_unicode,  False, 'application_url', 'http://glonull1.mobile.fp.nsn-rdnet.net:8080',
                                                                                        "URL under which app is running.")

    # misc
    _svd(config, t_bool, False, 'is_cost_center_visible_to_anyone',       False,        "True iff copy's cost center info is visible to anyone (= no perms required)")
    _svd(config, t_bool, True , 'display_tips',                            True,        "True iff tips are visible")
    _svd(config, t_bool, False, 'display_only_editable_config_options',    True,        "True iff user see only editable options.")
    _svd(config, t_unicode, False, 'default_go_back_link_name',         u'Back',     "Name of link displayed when filtering books/copies/...")
    return config
