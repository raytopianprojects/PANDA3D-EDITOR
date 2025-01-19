# global_registry.py

class GlobalRegistry:
    _registry = {}

    @classmethod
    def set_value(cls, key, value):
        cls._registry[key] = value

    @classmethod
    def get_value(cls, key):
        return cls._registry.get(key)

    @classmethod
    def remove_value(cls, key):
        if key in cls._registry:
            del cls._registry[key]
