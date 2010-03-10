#-*- coding=utf-8 -*- 

from django.db import models




class Book(models.Model):
    STATUS_CHOICES = (
            ('a', 'availalable'),
            ('d',  'disabled'),
        )
    #TODO: jakie rzeczywiście chcemy stany?
    # temporarily unavailable?
        

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    #TODO: jak długi tytuł/autor?
    author = models.CharField(max_length=50)
    localization = models.CharField(max_length=50, blank=True)
    #TODO: o co chodzi z localization?
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)
    
    def __unicode__(self):
        return u'id: ' + unicode(self.id) + u' ' + unicode(self.author) + u': ' + unicode(self.title)



class Person(models.Model):
    id = models.AutoField(primary_key=True)
    info = models.CharField(max_length=30)
    #TODO: jak rzeczywiście pracujemy z użytkownikiem

    def __unicode__(self):
        return u'id: ' + unicode(self.id) + u' ' + 'info: ' + unicode(self.info)


class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book)
    person = models.ForeignKey(Person)
    starts = models.DateField()
    expires = models.DateField()
    class Admin: pass

    def __unicode__(self):
        return u'id: ' + unicode(self.id) + u' ' + unicode(self.book) + u': reserved from ' + unicode(self.starts) + u' until ' + unicode(self.expires)
    

class Rental(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book)
    person = models.ForeignKey(Person)
    started = models.DateTimeField() #(auto_now_add=True)
    #who_handed_out = models.ForeignKey(Person)
    #TODO: czy chcemy automatyczne dodawanie bieżącej daty?
    ended = models.DateTimeField(blank=True, null=True)
    #TODO: id bibliotekarza?
    #who_received = models.ForeignKey(Person)

    def __unicode__(self):
        return u'id: ' + unicode(self.id) + u' ' + unicode(self.book) + u' rented ' + unicode(self.started) + u' to ' + unicode(self.person)




    
    

