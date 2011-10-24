# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Feedback'
        db.create_table('baseapp_feedback', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('who', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('msg', self.gf('django.db.models.fields.TextField')()),
            ('agent', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('baseapp', ['Feedback'])

        # Adding model 'EmailLog'
        db.create_table('baseapp_emaillog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sender', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('receiver', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('sent_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('body', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('baseapp', ['EmailLog'])

        # Adding model 'ConfigurationValueType'
        db.create_table('baseapp_configurationvaluetype', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20, primary_key=True)),
        ))
        db.send_create_signal('baseapp', ['ConfigurationValueType'])

        # Adding unique constraint on 'ConfigurationValueType', fields ['name']
        db.create_unique('baseapp_configurationvaluetype', ['name'])

        # Adding model 'Configuration'
        db.create_table('baseapp_configuration', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=60, primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('can_override', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['baseapp.ConfigurationValueType'])),
        ))
        db.send_create_signal('baseapp', ['Configuration'])

        # Adding model 'UserConfiguration'
        db.create_table('baseapp_userconfiguration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('option', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['baseapp.Configuration'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('baseapp', ['UserConfiguration'])

        # Adding unique constraint on 'UserConfiguration', fields ['option', 'user']
        db.create_unique('baseapp_userconfiguration', ['option_id', 'user_id'])

        # Adding model 'PhoneType'
        db.create_table('baseapp_phonetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('verify_re', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('baseapp', ['PhoneType'])

        # Adding unique constraint on 'PhoneType', fields ['name']
        db.create_unique('baseapp_phonetype', ['name'])

        # Adding model 'Phone'
        db.create_table('baseapp_phone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['baseapp.PhoneType'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('baseapp', ['Phone'])

        # Adding model 'UserProfile'
        db.create_table('baseapp_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('shoe_size', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('building', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['baseapp.Building'], null=True, blank=True)),
            ('awaits_activation', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('location_remarks', self.gf('django.db.models.fields.CharField')(max_length=70, null=True)),
        ))
        db.send_create_signal('baseapp', ['UserProfile'])

        # Adding unique constraint on 'UserProfile', fields ['user']
        db.create_unique('baseapp_userprofile', ['user_id'])

        # Adding M2M table for field phone on 'UserProfile'
        db.create_table('baseapp_userprofile_phone', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['baseapp.userprofile'], null=False)),
            ('phone', models.ForeignKey(orm['baseapp.phone'], null=False))
        ))
        db.create_unique('baseapp_userprofile_phone', ['userprofile_id', 'phone_id'])

        # Adding model 'Building'
        db.create_table('baseapp_building', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal('baseapp', ['Building'])

        # Adding unique constraint on 'Building', fields ['name']
        db.create_unique('baseapp_building', ['name'])

        # Adding model 'Location'
        db.create_table('baseapp_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('building', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['baseapp.Building'])),
            ('details', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=70, blank=True)),
        ))
        db.send_create_signal('baseapp', ['Location'])

        # Adding unique constraint on 'Location', fields ['building', 'details']
        db.create_unique('baseapp_location', ['building_id', 'details'])

        # Adding M2M table for field maintainer on 'Location'
        db.create_table('baseapp_location_maintainer', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('location', models.ForeignKey(orm['baseapp.location'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('baseapp_location_maintainer', ['location_id', 'user_id'])

        # Adding model 'State'
        db.create_table('baseapp_state', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('is_available', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_visible', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('baseapp', ['State'])

        # Adding unique constraint on 'State', fields ['name']
        db.create_unique('baseapp_state', ['name'])

        # Adding model 'Publisher'
        db.create_table('baseapp_publisher', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('baseapp', ['Publisher'])

        # Adding unique constraint on 'Publisher', fields ['name']
        db.create_unique('baseapp_publisher', ['name'])

        # Adding model 'Author'
        db.create_table('baseapp_author', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('baseapp', ['Author'])

        # Adding unique constraint on 'Author', fields ['name']
        db.create_unique('baseapp_author', ['name'])

        # Adding model 'Category'
        db.create_table('baseapp_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('baseapp', ['Category'])

        # Adding unique constraint on 'Category', fields ['name']
        db.create_unique('baseapp_category', ['name'])

        # Adding model 'Book'
        db.create_table('baseapp_book', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('baseapp', ['Book'])

        # Adding unique constraint on 'Book', fields ['title']
        db.create_unique('baseapp_book', ['title'])

        # Adding M2M table for field author on 'Book'
        db.create_table('baseapp_book_author', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('book', models.ForeignKey(orm['baseapp.book'], null=False)),
            ('author', models.ForeignKey(orm['baseapp.author'], null=False))
        ))
        db.create_unique('baseapp_book_author', ['book_id', 'author_id'])

        # Adding M2M table for field category on 'Book'
        db.create_table('baseapp_book_category', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('book', models.ForeignKey(orm['baseapp.book'], null=False)),
            ('category', models.ForeignKey(orm['baseapp.category'], null=False))
        ))
        db.create_unique('baseapp_book_category', ['book_id', 'category_id'])

        # Adding model 'BookRequest'
        db.create_table('baseapp_bookrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('who', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['baseapp.Book'], null=True, blank=True)),
            ('info', self.gf('django.db.models.fields.TextField')()),
            ('done', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('remarks', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('baseapp', ['BookRequest'])

        # Adding model 'CostCenter'
        db.create_table('baseapp_costcenter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('baseapp', ['CostCenter'])

        # Adding unique constraint on 'CostCenter', fields ['name']
        db.create_unique('baseapp_costcenter', ['name'])

        # Adding model 'BookCopy'
        db.create_table('baseapp_bookcopy', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shelf_mark', self.gf('django.db.models.fields.PositiveIntegerField')(unique=True)),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['baseapp.Book'])),
            ('cost_center', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['baseapp.CostCenter'])),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['baseapp.Location'])),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['baseapp.State'])),
            ('publisher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['baseapp.Publisher'], null=True, blank=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('publication_nr', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('toc', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('toc_url', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description_url', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
        ))
        db.send_create_signal('baseapp', ['BookCopy'])

        # Adding unique constraint on 'BookCopy', fields ['shelf_mark']
        db.create_unique('baseapp_bookcopy', ['shelf_mark'])

        # Adding model 'Reservation'
        db.create_table('baseapp_reservation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('book_copy', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['baseapp.BookCopy'])),
            ('for_whom', self.gf('django.db.models.fields.related.ForeignKey')(related_name='reader', to=orm['auth.User'])),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('who_reserved', self.gf('django.db.models.fields.related.ForeignKey')(related_name='reserver', to=orm['auth.User'])),
            ('when_reserved', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('who_cancelled', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='canceller', null=True, to=orm['auth.User'])),
            ('when_cancelled', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('active_since', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('shipment_requested', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('baseapp', ['Reservation'])

        # Adding model 'Rental'
        db.create_table('baseapp_rental', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reservation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['baseapp.Reservation'])),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('who_handed_out', self.gf('django.db.models.fields.related.ForeignKey')(related_name='giver', to=orm['auth.User'])),
            ('who_received', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='receiver', null=True, to=orm['auth.User'])),
        ))
        db.send_create_signal('baseapp', ['Rental'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'BookCopy', fields ['shelf_mark']
        db.delete_unique('baseapp_bookcopy', ['shelf_mark'])

        # Removing unique constraint on 'CostCenter', fields ['name']
        db.delete_unique('baseapp_costcenter', ['name'])

        # Removing unique constraint on 'Book', fields ['title']
        db.delete_unique('baseapp_book', ['title'])

        # Removing unique constraint on 'Category', fields ['name']
        db.delete_unique('baseapp_category', ['name'])

        # Removing unique constraint on 'Author', fields ['name']
        db.delete_unique('baseapp_author', ['name'])

        # Removing unique constraint on 'Publisher', fields ['name']
        db.delete_unique('baseapp_publisher', ['name'])

        # Removing unique constraint on 'State', fields ['name']
        db.delete_unique('baseapp_state', ['name'])

        # Removing unique constraint on 'Location', fields ['building', 'details']
        db.delete_unique('baseapp_location', ['building_id', 'details'])

        # Removing unique constraint on 'Building', fields ['name']
        db.delete_unique('baseapp_building', ['name'])

        # Removing unique constraint on 'UserProfile', fields ['user']
        db.delete_unique('baseapp_userprofile', ['user_id'])

        # Removing unique constraint on 'PhoneType', fields ['name']
        db.delete_unique('baseapp_phonetype', ['name'])

        # Removing unique constraint on 'UserConfiguration', fields ['option', 'user']
        db.delete_unique('baseapp_userconfiguration', ['option_id', 'user_id'])

        # Removing unique constraint on 'ConfigurationValueType', fields ['name']
        db.delete_unique('baseapp_configurationvaluetype', ['name'])

        # Deleting model 'Feedback'
        db.delete_table('baseapp_feedback')

        # Deleting model 'EmailLog'
        db.delete_table('baseapp_emaillog')

        # Deleting model 'ConfigurationValueType'
        db.delete_table('baseapp_configurationvaluetype')

        # Deleting model 'Configuration'
        db.delete_table('baseapp_configuration')

        # Deleting model 'UserConfiguration'
        db.delete_table('baseapp_userconfiguration')

        # Deleting model 'PhoneType'
        db.delete_table('baseapp_phonetype')

        # Deleting model 'Phone'
        db.delete_table('baseapp_phone')

        # Deleting model 'UserProfile'
        db.delete_table('baseapp_userprofile')

        # Removing M2M table for field phone on 'UserProfile'
        db.delete_table('baseapp_userprofile_phone')

        # Deleting model 'Building'
        db.delete_table('baseapp_building')

        # Deleting model 'Location'
        db.delete_table('baseapp_location')

        # Removing M2M table for field maintainer on 'Location'
        db.delete_table('baseapp_location_maintainer')

        # Deleting model 'State'
        db.delete_table('baseapp_state')

        # Deleting model 'Publisher'
        db.delete_table('baseapp_publisher')

        # Deleting model 'Author'
        db.delete_table('baseapp_author')

        # Deleting model 'Category'
        db.delete_table('baseapp_category')

        # Deleting model 'Book'
        db.delete_table('baseapp_book')

        # Removing M2M table for field author on 'Book'
        db.delete_table('baseapp_book_author')

        # Removing M2M table for field category on 'Book'
        db.delete_table('baseapp_book_category')

        # Deleting model 'BookRequest'
        db.delete_table('baseapp_bookrequest')

        # Deleting model 'CostCenter'
        db.delete_table('baseapp_costcenter')

        # Deleting model 'BookCopy'
        db.delete_table('baseapp_bookcopy')

        # Deleting model 'Reservation'
        db.delete_table('baseapp_reservation')

        # Deleting model 'Rental'
        db.delete_table('baseapp_rental')


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
