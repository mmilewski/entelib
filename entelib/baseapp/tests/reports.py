# -*- coding: utf-8 -*-
from django.test import TestCase
from baseapp.tests.page_logger import PageLogger
from baseapp.utils import pprint
from dbconfigfiller import fill_config
from baseapp.config import Config


class RenderingReportsTest(TestCase, PageLogger):
    '''
    Tests rendering reports. 
    '''

    fixtures = ['rentals_reservations.json', 'small_db-configuration.json', 'small_db-groups.json']

    def setUp(self):
        # self.config = fill_config()
        self.config = Config()
        self.login('superadmin', 'superadmin')
    
    def get_post_data_for_report_type(self, report_type):
        return {'report_type': report_type, 'action': 'show', 'from':'', 'to':''}
    
    def test_render_library_status(self):
        ''' Checks if 'library status' report renders.'''
        response = self.client.get('/entelib/report/status/')
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'reports/library_status.html')
        
    def test_render_most_often_rented(self):
        ''' Checks if 'most often rented books' report renders.'''
        response = self.client.get('/entelib/report/most_often_rented/')
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'reports/most_often_rented.html')
        
    def test_render_most_often_reserved(self):
        ''' Checks if 'most often reserved books' report renders.'''
        response = self.client.get('/entelib/report/most_often_reserved/')
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'reports/most_often_reserved.html')
        
    def test_render_user_black_list(self):
        ''' Checks if 'user black list' report renders.'''
        response = self.client.get('/entelib/report/black_list/')
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'reports/black_list.html')
        
    def test_render_unavailable_books(self):
        ''' Checks if 'unavailable books' report renders.'''
        response = self.client.get('/entelib/report/lost_books/')
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'reports/library_status.html')
        
