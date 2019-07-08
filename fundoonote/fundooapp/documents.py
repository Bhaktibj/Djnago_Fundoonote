from django_elasticsearch_dsl import DocType, Index, fields

from .index import note_index, html_strip
from .models import Notes
from elasticsearch_dsl.connections import connections
""" ElasticSearch function"""
connections.create_connection(hosts=['localhost'])
connections.get_connection().cluster.health()
notes = Index('notes')
@note_index.doc_type
class NotesDocument(DocType):
    title = fields.StringField(
        analyzer=html_strip,
        fields={
            'raw': fields.StringField(analyzer='keyword'),

        }
    )
    description = fields.StringField(
        analyzer=html_strip,
        fields={
            'raw': fields.StringField(analyzer='keyword'),

        }
    )
    color = fields.StringField(
        analyzer=html_strip,
        fields={
            'raw': fields.StringField(analyzer='keyword'),
        }
    )
    remainder = fields.StringField(
        analyzer=html_strip,
        fields={
            'raw': fields.StringField(analyzer='keyword'),
        }
    )

    class Meta(object):
        model = Notes