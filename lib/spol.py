from lib.JBConfigParser import JBConfigParser,JBSectionHandler

cfg:JBConfigParser=None
"""Správa konfiguračního souboru"""

cfgMain:JBSectionHandler=None
"""Sekce main v konfiguračním souboru"""

run_dir:str=None

touch_file_path:str=None