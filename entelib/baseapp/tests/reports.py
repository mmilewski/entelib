# -*- coding: utf-8 -*-
from django.test import TestCase
from baseapp.tests.page_logger import PageLogger
from baseapp.utils import pprint
from dbconfigfiller import fill_config


class RenderingReportsTest(TestCase, PageLogger):
    '''
    Tests rendering reports. 
    '''

    fixtures = ['rentals_reservations.json']

    def setUp(self):
        self.config = fill_config()
        self.login('superadmin', 'superadmin')
    
    def get_post_data_for_report_type(self, report_type):
        return {'report_type': report_type, 'action': 'show', 'from':'', 'to':''}
    
    def test_render_library_status(self):
        ''' Checks if 'library status' report renders.'''
        response = self.client.post('/entelib/report/', self.get_post_data_for_report_type('status'))
        self.assertEquals(200, response.status_code)
        
    def test_render_most_often_rented(self):
        ''' Checks if 'most often rented books' report renders.'''
        response = self.client.post('/entelib/report/', self.get_post_data_for_report_type('most_often_rented'))
        self.assertEquals(200, response.status_code)
        
    def test_render_most_often_reserved(self):
        ''' Checks if 'most often reserved books' report renders.'''
        response = self.client.post('/entelib/report/', self.get_post_data_for_report_type('most_often_reserved'))
        self.assertEquals(200, response.status_code)
        
    def test_render_user_black_list(self):
        ''' Checks if 'user black list' report renders.'''
        response = self.client.post('/entelib/report/', self.get_post_data_for_report_type('black_list'))
        self.assertEquals(200, response.status_code)
        
    def test_render_unavailable_books(self):
        ''' Checks if 'unavailable books' report renders.'''
        response = self.client.post('/entelib/report/', self.get_post_data_for_report_type('lost_books'))
        self.assertEquals(200, response.status_code)
        
