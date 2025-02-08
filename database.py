import csv

class DatabaseFile:
    def __init__(self, filePath:str):
        self.path = filePath
        self.activeconncetion = None
        self.lock = False
        self.cache = {}
    
    def change_mode(self, mode:str):
        self.disconnect()
        self.connect(mode)

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

        self.change_mode('r')
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

    def build_new_array(self, exceptions, extra_data):
        self.change_mode('r')
        new_data = []
        reader = csv.reader(self.activeconncetion)
        for i, row in enumerate(reader):
            if not row in exceptions:
                new_data.append(row)
        
        new_data.append(extra_data)
        
        return new_data

    def write_back(self, data:list[list]):
        self.change_mode("a")
        self.activeconncetion.truncate(0)

        writer = csv.reader(self.activeconncetion)
        for i, row in enumerate(data):
            writer.writerow(row)

    def write(self, key:str, value, notexists:bool):
        if notexists and len(self.find_existing_keys(key)) > 0:
            return "Already exists"
        
        self.change_mode('w')
        self.build_new_array(extra_data=value)

        writer = csv.writer(self.activeconncetion)
        writer.writerow([key, data])

        self.cache_value(key, data)

    def read(self, key:str, keyrow=0):
        cachedata = self.read_cache(key)
        if cachedata is not None:
            return cachedata
        
        self.change_mode('r')
        reader = csv.reader(self.activeconncetion)
        for row in reader():
            if row[keyrow] == key:
                return row
        
        return None
