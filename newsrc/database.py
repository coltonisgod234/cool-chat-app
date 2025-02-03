import csv

class DatabaseFile:
    def __init__(self, filePath:str):
        self.path = filePath
        self.activeconncetion = None
        self.lock = False
        self.cache = {}
    
    def connect(self, mode:str):
        if self.lock == True:
            return None

        self.activeconncetion = open(self.path, mode)
        self.lock = True

        return self.activeconncetion  # This is a REFRENCE and NOT A COPY!
    
    def disconnect(self):
        self.activeconncetion.close()  # THIS UPDATES ALL INSTANCES, SPOOKY~~
        self.lock = False
    
    def cache_value(self, key, value):
        self.cache[key] = value
    
    def read_cache(self, key):
        try: return self.cache[key]
        except: return None

    def find_existing_keys(self, key, keyrow=0):
        cachedata = self.read_cache(key)
        if cachedata is not None:
            return cachedata

        results = []  # Using a list to allow searching for conflcits
        reader = csv.reader(self.activeconncetion)
        for i,row in enumerate(reader):
            if row[keyrow] == key:
                results.append(i)

        return results

    def list_to_csv(self, l:list):
        s = ""
        for i in l:
            s.__add__(f"{i},")
        
        return s

    def write(self, key:str, value, notexists:bool):
        if notexists and len(self.find_existing_keys(key)) > 0:
            return "Already exists"
        
        writer = csv.writer(self.activeconncetion)
        if isinstance(value, list):
            data = self.list_to_csv(value)
        elif isinstance(value, str):
            data = value

        writer.writerow([key, data])

        self.cache_value(key, data)

    def read(self, key:str, keyrow=0):
        cachedata = self.read_cache(key)
        if cachedata is not None:
            return cachedata
        
        reader = csv.reader(self.activeconncetion)
        for row in reader():
            if row[keyrow] == key:
                return row
        
        return None
    
    def delete(self, key:str, keyrow=0, occurence=0):
        '''
        Delete the first Nth of `key` in the file
        '''
        keys = self.find_existing_keys(key, keyrow)
        k = keys[0]

        new_data = []
        reader = csv.reader(self.activeconncetion)
        for i, row in enumerate(reader):
            if not i == k:
                new_data.append(row)
