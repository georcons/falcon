#
# If you create new pipes you MUST update this table
PIPES_SOURCES = {
    "OpenAI": ".gptpipe",
    "Together": ".together"
}

def retrieve_model_source(name):
    return PIPES_SOURCES[name] if name in PIPES_SOURCES else None

def _get_pipes():
    return list(PIPES_SOURCES.keys())