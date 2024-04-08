import configparser,logging

log=logging.getLogger('iniParser')

class JBConfigParser(configparser.ConfigParser):
    __fullFileName:str=""
    """Plná cesta k souboru i s jeho jménem"""
    
    __autoSave:bool=None
    
    def __init__(self, fullPathAndName:str,autoSave:bool=True):
        self.__fullFileName=fullPathAndName      
        self.__autoSave=autoSave
        super().__init__()
        self.load()
    
    def get_section(self, section:str, autoCreate:bool=False):
        """Vrátí objekt pro snadnější práci se sekcí.
        Pokud sekce neexistuje a autoCreate je True, sekce bude vytvořena.

        Args:
            section (str): Název sekce
            autoCreate (bool, optional): Pokud sekce neexistuje a autoCreate je True, sekce bude vytvořena, jinak vrátí False

        Returns:
            JBSectionHandler: JBSectionHandler pokud sekce existuje, nebo byla vytvořena, jinak None
        """        
        cr = self.has_section(section)
        if autoCreate:
            if not cr:
                try:
                    self.add_section(section)
                    self.__saveIfRq()
                except Exception as e:
                    log.exception("Výjimka")
                    return None
        else:
            if not cr:
                return None
            
        return JBSectionHandler(self, section)
    
    def load(self):
        """Načte soubor, pokud byly v paměti provedené změny tak budou přepsány stavem ze souboru"""
        self.read(self.__fullFileName)
    
    def save(self):
        """Uloží aktuální hodnoty v paměti do souboru"""
        with open(self.__fullFileName, 'w') as configfile:
            self.write(configfile)
            
    def __saveIfRq(self):
        if self.__autoSave:
            self.save()
                    
              
class JBSectionHandler:
    """Třída pro zjednodušenou práci s konkrétní sekci."""
    
    __config:JBConfigParser=None
    
    def __init__(self, config, section):
        self.__config = config
        self.section = section

    def get(self, key, fallback=None)->str:
        """Vrátí str hodnotu pro daný klíč s možností výchozí hodnoty."""
        x=self.__config.get(self.section, key, fallback=fallback)
        return x
    
    def getInt(self, key, fallback=None)->int:
        """Vrátí hodnotu pro daný klíč s možností výchozí hodnoty."""
        x=self.__config.get(self.section, key, fallback=fallback)
        try:
            x=int(x)
        except Exception as e:
            log.exception('Výjimka převodu na INT')
        return x
            
    def getFloat(self, key, fallback=None)->float:
        """Vrátí hodnotu pro daný klíč s možností výchozí hodnoty."""
        x=self.__config.get(self.section, key, fallback=fallback)
        try:
            x=float(x)
        except Exception as e:
            log.exception('Výjimka převodu na float')
            x=fallback
        return x
            
    def getBool(self, key, fallback=None)->bool:
        """Vrátí hodnotu pro daný klíč s možností výchozí hodnoty."""
        val = self.__config.get(self.section, key, fallback=str(fallback)).lower()
        return val in ["true", "1", "yes", "on"]
    
    def set(self, key, value):
        """Nastaví hodnotu pro daný klíč"""
        x=self.__config.set(self.section, key, value)
        self.__config.__saveIfRq()
        return x
