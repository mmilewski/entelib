# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'TemporaryLocationMaintainer.adder'
        db.add_column('baseapp_temporarylocationmaintainer', 'adder', self.gf('django.db.models.fields.related.ForeignKey')(related_name='adder', to=orm['auth.User']), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'TemporaryLocationMaintainer.adder'
        db.delete_column('baseapp_temporarylocationmaintainer', 'adder_id')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '70'})
        },
        'baseapp.author': {
            'Meta': {'unique_together': "(('name',),)", 'object_name': 'Author'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'baseapp.book': {
            'Meta': {'unique_together': "(('title',),)", 'object_name': 'Book'},
            'author': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['baseapp.Author']", 'symmetrical': 'False'}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['baseapp.Category']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'baseapp.bookcopy': {
            'Meta': {'unique_together': "(('shelf_mark',),)", 'object_name': 'BookCopy'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['baseapp.Book']"}),
            'cost_center': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['baseapp.CostCenter']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_url': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['baseapp.Location']"}),
            'publication_nr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'publisher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['baseapp.Publisher']", 'null': 'True', 'blank': 'True'}),
            'shelf_mark': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['baseapp.State']"}),
            'toc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'toc_url': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'baseapp.bookrequest': {
            'Meta': {'object_name': 'BookRequest'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['baseapp.Book']", 'null': 'True', 'blank': 'True'}),
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {}),
            'remarks': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'who': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'baseapp.building': {
            'Meta': {'unique_together': "(('name',),)", 'object_name': 'Building'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        'baseapp.category': {
            'Meta': {'unique_together': "(('name',),)", 'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'baseapp.configuration': {
            'Meta': {'object_name': 'Configuration'},
            'can_override': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '60', 'primary_key': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['baseapp.ConfigurationValueType']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'baseapp.configurationvaluetype': {
            'Meta': {'unique_together': "(('name',),)", 'object_name': 'ConfigurationValueType'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'primary_key': 'True'})
        },
        'baseapp.costcenter': {
            'Meta': {'unique_together': "(('name',),)", 'object_name': 'CostCenter'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'baseapp.emaillog': {
            'Meta': {'object_name': 'EmailLog'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'receiver': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sender': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sent_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'baseapp.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'agent': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'msg': ('django.db.models.fields.TextField', [], {}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'who': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'baseapp.location': {
            'Meta': {'ordering': "['building__name', 'details']", 'unique_together': "(('building', 'details'),)", 'object_name': 'Location'},
            'building': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['baseapp.Building']"}),
            'details': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintainer': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'})
        },
        'baseapp.phone': {
            'Meta': {'object_name': 'Phone'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['baseapp.PhoneType']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'baseapp.phonetype': {
            'Meta': {'unique_together': "(('name',),)", 'object_name': 'PhoneType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'verify_re': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'baseapp.publisher': {
            'Meta': {'unique_together': "(('name',),)", 'object_name': 'Publisher'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'baseapp.rental': {
            'Meta': {'object_name': 'Rental'},
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reservation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['baseapp.Reservation']"}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'who_handed_out': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'giver'", 'to': "orm['auth.User']"}),
            'who_received': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'receiver'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'baseapp.reservation': {
            'Meta': {'object_name': 'Reservation'},
            'active_since': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'book_copy': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['baseapp.BookCopy']"}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'for_whom': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reader'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shipment_requested': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'when_cancelled': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'when_reserved': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'who_cancelled': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'canceller'", 'null': 'True', 'to': "orm['auth.User']"}),
            'who_reserved': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reserver'", 'to': "orm['auth.User']"})
        },
        'baseapp.state': {
            'Meta': {'unique_together': "(('name',),)", 'object_name': 'State'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'baseapp.temporarylocationmaintainer': {
            'Meta': {'object_name': 'TemporaryLocationMaintainer'},
            'adder': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'adder'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['baseapp.Location']"}),
            'maintainer': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'})
        },
        'baseapp.userconfiguration': {
            'Meta': {'unique_together': "(('option', 'user'),)", 'object_name': 'UserConfiguration'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['baseapp.Configuration']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'baseapp.userprofile': {
            'Meta': {'unique_together': "(('user',),)", 'object_name': 'UserProfile'},
            'awaits_activation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['baseapp.Building']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location_remarks': ('django.db.models.fields.CharField', [], {'max_length': '70', 'null': 'True'}),
            'phone': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['baseapp.Phone']", 'null': 'True', 'blank': 'True'}),
            'shoe_size': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['baseapp']
