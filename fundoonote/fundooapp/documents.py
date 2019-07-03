from django_elasticsearch_dsl import DocType, Index
from .models import Notes

notes = Index('notes')

@notes.doc_type
class PostDocument(DocType):
    class Meta:
        model = Notes

        fields = [
            'title',
            'description',
            'id',
            'image',
        ]