# -*- coding: utf-8 -*-

from django.contrib.auth.models import Permission
from django.db.models import Q

admins_perms     = Permission.objects.filter(~Q(codename__icontains='delete'))     # superadmin can delete, admin does not

readers_perms    = ['list_books', 'view_own_profile', 'add_reservation', 'change_own_reservation', 'add_bookrequest',
                    'list_config_options', 'edit_option',
                    'list_locations', 'view_location',

                    'view_category',   # 'list_categories',
                    'view_author',     # 'list_authors',
                    'view_publisher',  # 'list_publishers',
                    'view_costcenter', 
                    'view_building',   # 'list_buildings',
                    ]
readers_perms = [ Permission.objects.get(codename=pname) for pname in readers_perms ]

librarians_perms = ['list_users', 'list_reports',
                    'list_costcenters',
                    'list_authors', 'list_publishers', 'list_categories',
                    'add_rental', 'change_rental', 'change_reservation', 
                    'add_book', 'change_book',
                    'add_bookcopy', 'change_bookcopy',
                    'add_author', 'change_author',
                    'add_category', 'change_category',
                    'add_publisher', 'change_publisher',
                    'add_costcenter', 'change_costcenter',
                    
                    'view_bookrequest', 'list_bookrequests',  'change_bookrequest', 
                    'view_category',   'list_categories',
                    'view_author',     'list_authors',
                    'view_publisher',  'list_publishers',
                    'view_costcenter', 
                    'view_building',   'list_buildings',
                    ]
librarians_perms = [ Permission.objects.get(codename=pname) for pname in librarians_perms ]
librarians_perms = librarians_perms + readers_perms

groups = { 'librarians': 'Librarians',  'admins': 'Admins',  'readers': 'Readers' }
perms_by_group = { groups['admins']: admins_perms,
                   groups['readers']: readers_perms,
                   groups['librarians']: librarians_perms }
