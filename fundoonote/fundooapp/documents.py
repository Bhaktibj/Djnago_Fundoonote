from django_elasticsearch_dsl import DocType, Index, fields
from elasticsearch_dsl.connections import connections
from .index import note_index, html_strip
from .models import Notes
# connections.create_connection(hosts=['localhost'])
# connections.get_connection().cluster.health()
"""cluster:A cluster is a collection of one or more nodes (servers), 
   that together holds your entire data.
analyzer:The keyword analyzer is a “noop” analyzer that accepts whatever text, 
         it is given and outputs the exact same text as a single term.
Document:A document is a basic unit of information that can be indexed """
notes = Index('notes')
@note_index.doc_type
class NotesDocument(DocType):
    """ This DocType class is used to creating the index"""
    title = fields.StringField(
        analyzer=html_strip,
        fields={
            'raw': fields.StringField(analyzer='keyword'),

        }
    )
    # based on description field Documents
    description = fields.StringField(
        analyzer=html_strip,
        fields={
            'raw': fields.StringField(analyzer='keyword'),

        }
    )
    # based on color field Documents
    color = fields.StringField(
        analyzer=html_strip,
        fields={
            'raw': fields.StringField(analyzer='keyword'),
        }
    )
    # based on Reminder field Documents
    remainder = fields.StringField(
        analyzer=html_strip,
        fields={
            'raw': fields.StringField(analyzer='keyword'),
        }
    )
    class Meta(object):
        """taking the object from Notes Model"""
        model = Notes

print('NotesDocument:', NotesDocument.__doc__)

