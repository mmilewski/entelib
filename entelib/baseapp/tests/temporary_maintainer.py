# -*- coding: utf-8 -*-
from django.test import TestCase
from views import TestWithSmallDB
from ExtraAsserts import ExtraAsserts
from django.contrib.auth.models import User, UserManager
from baseapp.models import TemporaryLocationMaintainer, Location, User, Building
from baseapp.views_aux import get_maintainers_description_for_location, \
                              get_maintainers_for_location, \
                              add_temporary_maintainer_for_location, \
                              remove_temporary_maintainer_from_location, \
                              CannotManageMaintainers


class GettingMaintaingersFromLocation(TestWithSmallDB, ExtraAsserts):
    def setUp(self):
        self.email_autoincrement = 0    # emails must be unique. This guarantes that
        building = Building(name='Bema')
        building.save()
        self.loc = Location(building=building, details="A location")
        self.loc.save()

    def create_user(self, username=None):
        '''
        Factory of users.
        '''
        self.email_autoincrement += 1
        email = 'some@mail.com-' + str(self.email_autoincrement)
        password = email
        if username is None:
            username = 'user-' + str(self.email_autoincrement)
        u = User.objects.create_user(username, email, password)
        u.save()
        return u

    def create_tmploc(self, location, users):
        '''
        If location is instance of Location then return TemporaryLocationMaintainer with location set to it.
        Otherwise, creates NEW Location instance with location as its name.
        '''
        adder = self.create_user('Adder')
        if isinstance(location, Location):
            t = TemporaryLocationMaintainer(location=location, adder=adder)
            t.save()
            for user in users:
                t.maintainer.add(user)
            return t
        else:
            b = Building(name='Some building')
            b.save()
            location = Location(building=b, details=location)
            location.save()
            t = TemporaryLocationMaintainer(location=location)
            t.save()
            for user in users:
                t.maintainer.add(user)
            return t

    def test_can_add_user_to_location_maintainers(self):
        loc = self.loc
        user = User.objects.get(pk=2)

        self.assert_(loc)
        self.assert_(user)

        a = loc.maintainer.count()
        loc.maintainer.add(user)
        b = loc.maintainer.count()

        self.assertEqual(a, 0)
        self.assertEqual(b, 1)

    def test_get_maintainers_returns_correct_dict_from_real_maintainers(self):
        loc = self.loc
        user = self.create_user()

        loc.maintainer.add(user)
        actual = get_maintainers_description_for_location(loc)

        expected = [ {'user':user, 'temporary':False} ]
        self.assertEqual(actual, expected)
        self.assertEqual(get_maintainers_for_location(loc)[0], user)

    def test_get_maintainers_returns_temporary_maintainer(self):
        tmpuser = self.create_user()
        tmploc = self.create_tmploc(self.loc, [tmpuser])

        self.assertEqual(tmploc.maintainer.count(), 1)
        self.assertEqual(self.loc, tmploc.location)

        actual = get_maintainers_description_for_location(self.loc)
        expected = [ {'user':tmpuser, 'temporary':True} ]

        self.assertEqual(actual, expected)
        self.assertEqual(get_maintainers_for_location(self.loc)[0], tmpuser)

    def test_get_maintainers_returns_dict_containing_all_temporary_maintainers(self):
        loc = self.loc
        user = self.create_user()
        tmpusers = [self.create_user(), self.create_user()]

        loc.maintainer.add(user)
        tmploc = self.create_tmploc(loc, tmpusers)
        actual = get_maintainers_description_for_location(loc)

        expected = [ {'user':u, 'temporary':True} for u in tmpusers ] + [ {'user':user, 'temporary':False} ]
        self.assertSetEqual(actual, expected)

    def test_adding_maintainer_for_location_by_forbidden_user(self):
        '''
        If user is not location real maintainer then he cannot add temporary maintainers for this location.
        '''
        location = self.loc
        maintainer = self.create_user()
        adder = self.create_user()
        tmplocation = self.create_tmploc(location, [])

        self.assertRaises(CannotManageMaintainers, add_temporary_maintainer_for_location, tmplocation, maintainer, adder)

    def test_adding_maintainer_for_location_by_permitted_user(self):
        '''
        If user is not location's real maintainer, then he cannot add temporary maintainers for this location.
        '''
        location = self.loc
        maintainer = self.create_user()
        adder = self.create_user('adder')
        location.maintainer.add(adder)
        tmplocation = self.create_tmploc(location, [])

        add_temporary_maintainer_for_location(tmplocation, maintainer, adder)

        maintainers = get_maintainers_description_for_location(location)
        self.assertIn( {'user':maintainer, 'temporary':True}, maintainers)
        self.assertIn( maintainer, get_maintainers_for_location(location) )

    def test_removing_maintainer_for_location_by_forbidden_user(self):
        location = self.loc
        maintainer = self.create_user('main')
        remover = self.create_user('remover')
        tmplocation = self.create_tmploc(location, [maintainer])

        self.assertRaises(CannotManageMaintainers, remove_temporary_maintainer_from_location, tmplocation, maintainer, remover)

    def test_removing_maintainer_for_location_by_permitted_user(self):
        '''
        If user is not location's real maintainer, then he cannot remove temporary maintainers for this location.
        '''
        location = self.loc
        maintainer = self.create_user('main')
        remover = self.create_user('remover')
        location.maintainer.add(remover)
        tmploc = self.create_tmploc(location, [maintainer])

        remove_temporary_maintainer_from_location(tmploc, maintainer, remover)

        maintainers = get_maintainers_description_for_location(location)
        self.assertNotIn( {'user':maintainer, 'temporary':True}, maintainers)
        self.assertNotIn( maintainer, maintainers )
