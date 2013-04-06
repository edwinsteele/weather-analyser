__author__ = 'esteele'

from base_retrievers import AbstractRetriever


class MetwitRetriever(AbstractRetriever):
    """
    http://metwit.com/developers/docs/
    """
    @property
    def source(self):
        return "metwit"

