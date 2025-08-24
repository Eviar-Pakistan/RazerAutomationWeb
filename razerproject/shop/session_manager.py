import requests

class RazerSessionManager:
    _session = None
    _store = {}

    @classmethod
    def get_session(cls):
        if cls._session is None:
            cls._session = requests.Session()
        return cls._session

    @classmethod
    def set_session(cls, session_obj):
        if isinstance(session_obj, requests.Session):
            cls._session = session_obj
        else:
            raise TypeError("Expected a requests.Session object")

    @classmethod
    def reset_session(cls):
        cls._session = requests.Session()
        cls._store = {}

    @classmethod
    def set(cls, key, value):
        cls._store[key] = value

    @classmethod
    def get(cls, key, default=None):
        return cls._store.get(key, default)

    @classmethod
    def all(cls):
        return cls._store.copy()
