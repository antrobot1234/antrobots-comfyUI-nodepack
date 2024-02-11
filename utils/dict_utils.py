from collections import UserDict
class Entry:
    def __init__(self, value = None, typedef = None, default = None):
        if typedef == None and value == None and default == None: raise Exception("Must specify at least one of value, typedef, or default")
        if default != None and value == None: value = default
        if value != None:
            if typedef != None: 
                try: value = typedef(value)
                except: raise Exception(f"Could not convert {value} to {typedef}")
            else: typedef = type(value)
        if typedef != None:
            try: default = typedef() if default == None else typedef(default)
            except: print("could not populate default")
        
        self.typedef = typedef
        self.default = default
        self.value = value
    def __repr__(self) -> str:
        return f"Entry(value={self.value}, typedef={self.typedef}, default={self.default})"
    def is_type(self, type):
        return self.typedef == type
    def get_value(self):
        if self.value == None: return self.default
        return self.value
class EntryDict(UserDict):
    def __setitem__(self, key,item) -> None:
        if not isinstance(item, Entry):
            try:
                if isinstance(item, dict):item = Entry(**item)
                else:item = Entry(item)
            except ValueError:
                raise Exception(f"Could not convert {item} to Entry")
        return super().__setitem__(key, item)
    def get_by_reference(self, key, reference : Entry) -> Entry:
        entry = self.get(key, reference)
        if entry is not reference:
            if entry.is_type(reference.typedef):
                return entry
            else: raise Exception(f"Entry {key} is not {reference.typedef.__name__}")
        return entry