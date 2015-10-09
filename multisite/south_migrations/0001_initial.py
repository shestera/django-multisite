# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):
    def forwards(self, orm):
        """Create Alias table."""

        # Adding model 'Alias'
        db.create_table('multisite_alias', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['sites.Site'])),
            ('domain', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('is_canonical', self.gf('django.db.models.fields.NullBooleanField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal('multisite', ['Alias'])

        # Adding unique constraint on 'Alias',
        # fields ['is_canonical', 'site']
        db.create_unique('multisite_alias', ['is_canonical', 'site_id'])

    def backwards(self, orm):
        """Drop Alias table."""

        # Removing unique constraint on 'Alias',
        # fields ['is_canonical', 'site']
        db.delete_unique('multisite_alias', ['is_canonical', 'site_id'])

        # Deleting model 'Alias'
        db.delete_table('multisite_alias')

    models = {
        'multisite.alias': {
            'Meta': {'unique_together': "[('is_canonical', 'site')]", 'object_name': 'Alias'},
            'domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_canonical': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': "orm['sites.Site']"})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['multisite']
