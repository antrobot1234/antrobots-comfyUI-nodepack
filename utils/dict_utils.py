class Entry:
    def __init__(self, key, value = None, typedef = None, default = None):
        if value != None:
            if typedef != None: 
                try: value = typedef(value)
                except: raise Exception(f"Could not convert {value} to {typedef}")
            else: typedef = type(value)
        if typedef != None:
            try: default = typedef() if default == None else typedef(default)
            except: raise Exception(f"Could not convert {default} to {typedef}")
        
        self.key = key
        self.typedef = typedef
        self.default = default
        self.value = value