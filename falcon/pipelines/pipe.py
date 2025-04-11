import importlib
from .pipes_list import _get_pipes
from .pipes_list import retrieve_model_source

class Pipeline:
    def __init__(self, pipe_name):
        source = retrieve_model_source(pipe_name)
        if source == None:
            return
        self.PIPE_NAME = pipe_name
        __parent__ = __name__[:__name__.rfind('.'):]
        PIPE_ENTIRE_MODULE = importlib.import_module(source, package=__parent__)
        self.retrieve_response = PIPE_ENTIRE_MODULE.retrieve_response
        self.send_batch = PIPE_ENTIRE_MODULE.send_batch
        self.retrieve_batch = PIPE_ENTIRE_MODULE.retrieve_batch
        self.DEF_MODEL = PIPE_ENTIRE_MODULE.DEF_MODEL
        self.DEF_TEMPERATURE = PIPE_ENTIRE_MODULE.DEF_TEMPERATURE

    @staticmethod
    def get_pipes():
        return _get_pipes()