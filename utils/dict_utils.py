from collections import UserDict
class Entry:
    def __init__(self, value = None, typedef = None, default = None):
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
class EntryDict(UserDict):
    def __setitem__(self, key,item) -> None:
        if not isinstance(item, Entry):
            try:
                if isinstance(item, dict):item = Entry(**item)
                else:item = Entry(item)
            except: raise Exception(f"Could not convert {item} to Entry")
        return super().__setitem__(key, item)

entry_dict = EntryDict()
entry_dict["a"] = {"value":29}
print(entry_dict["a"])