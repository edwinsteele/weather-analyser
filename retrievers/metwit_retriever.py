__author__ = 'esteele'

from abstract_http_retriever import AbstractHTTPRetriever


class MetwitRetriever(AbstractHTTPRetriever):
    """
    http://metwit.com/developers/docs/
    """
    @property
    def source(self):
        return "metwit"

