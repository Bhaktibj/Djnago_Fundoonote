from elasticsearch_dsl import analyzer
from django_elasticsearch_dsl import Index

""" 
html_strip: The html_strip character filter strips HTML elements from the text.
index : An index is a collection of documents.
tokenizer : A tokenizer receives a stream of characters, breaks it up into individual
            tokens (usually individual words),and outputs a stream of tokens. 
number_of_shards : It allows you to horizontally split/scale your content volume.
number_of_replicas : It provides high availability in case a shard/node fails.  

"""
""" Create the Index """
note_index = Index('notes')
note_index.settings(
    number_of_shards=1,
    number_of_replicas=1
    )
html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
    )
