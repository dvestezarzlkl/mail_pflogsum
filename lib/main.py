import subprocess, datetime, logging, os
from lib.JBConfigParser import JBConfigParser
import lib.helper as helper,lib.spol as spol

log = logging.getLogger("main")

def getCFG()->JBConfigParser:
    return spol.cfg.get_section("MAIL",True)

def should_rotate() -> bool:
    # Získání aktuálního data
    now = datetime.datetime.now()
    today = now.date()
    
    # Kontrola, zda touch soubor existuje
    if os.path.exists(spol.touch_file_path):
        # Získání data poslední modifikace souboru
        file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(spol.touch_file_path))
        file_mod_date = file_mod_time.date()
        
        # Kontrola, zda byla rotace již provedena dnes
        if file_mod_date == today and now.hour == 0:
            # Rotace už byla dnes provedena, nebudeme rotovat znovu
            return False
    elif now.hour <5: # pokud je méně než 5. hodina, tak rotujeme
        return False
    return True

def send_email_statistics(rotate: bool)->bool:
    try:
        cfg:JBConfigParser = getCFG()
        log.info("Odesílám email s logem")

        tomail = cfg.get('to',None)
        frommail = cfg.get('from',None)
        nameserver = spol.cfgMain.get('nameserver',None)
        host = cfg.get('host',None)
        port = cfg.getInt('port',587)
        pwd = cfg.get('pwd','')

        if tomail is None or frommail is None or nameserver is None or host is None or port is None:
            log.error("Není nastavena konfigurace pro odesílání emailů")
            return False

        subj = " - log rotated" if rotate else " - rotated not need"
        subj = f"Subject: Mail Statistics {nameserver} server : {subj}"

        try:
            verb_det=cfg.getInt('verbose_msg_detail',0)
            arg=['pflogsumm']
            if verb_det==1:
                arg.append('--verbose_msg_detail')
                log.info("Přidávám verbose_msg_detail")
            else:
                log.info("Nepřidávám verbose_msg_detail")
            arg.append('/var/log/mail.log')

            # Spuštění pflogsumm a zachycení výstupu
            log.info(f"Spouštím příkaz: {' '.join(arg)}")
            result = subprocess.run(arg, capture_output=True, text=True, check=True)
            result=f"<pre>{result.stdout}</pre>"
        except subprocess.CalledProcessError as e:
            log.exception("Chyba při spouštění pflogsumm")
            return False

        if helper.send_html_email(subj, result, tomail, frommail, pwd, host, port):
            log.info("Email byl odeslán se subjektem: "+subj)
            return True
        else:
            log.error("Email nebyl odeslán")
            return False
    except Exception as e:
        log.exception("Výjimka při odesílání emailu")
        return False

def rotate_logs(logrotate_conf_path:str)->bool:
    if should_rotate():
        try:
            subprocess.run(f"logrotate -vf {logrotate_conf_path}", shell=True, check=True)
            subprocess.run("chmod 644 /var/log/mail.log", shell=True, check=True)
            log.info("Log byl zrotován, updatuji touch soubor")

            # Aktualizace/znovu vytvoření touch souboru s aktuálním datem
            with open(spol.touch_file_path, 'a'):  # 'a' pro append, vytvoří soubor, pokud neexistuje
                os.utime(spol.touch_file_path)  # Aktualizace časových razítek na aktuální čas
            return True
        except subprocess.CalledProcessError as e:
            log.error(f"Chyba při rotaci logu: {e.output}")
            return False
        except Exception as e:
            log.error(f"Výjimka při rotaci logu: {e}")
            return False
