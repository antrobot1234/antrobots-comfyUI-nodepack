from collections import UserDict
class Entry:
    def __init__(self, value = None, typedef = None, default = None):
        if typedef == None and value == None: raise Exception("Either a type or a value must be provided")
        if value != None:
            if typedef != None: 
                try: value = typedef(value)
                except: raise Exception(f"Could not convert {value} to {typedef}")
            else: typedef = type(value)
        if typedef != None:
            try: default = typedef() if default == None else typedef(default)
            except: raise Exception(f"Could not convert {default} to {typedef}")
        
        self.typedef = typedef
        self.default = default
        self.value = value
    def __repr__(self) -> str:
        return f"Entry(value={self.value}, typedef={self.typedef}, default={self.default})"
    def is_type(self, type):
        return self.typedef == type
class EntryDict(UserDict):
    def __setitem__(self, key,item) -> None:
        if not isinstance(item, Entry):
            try:
                if isinstance(item, dict):item = Entry(**item)
                else:item = Entry(item)
            except ValueError:
                raise Exception(f"Could not convert {item} to Entry")
        return super().__setitem__(key, item)