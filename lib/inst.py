from crontab import CronTab
import os, shutil, logging
import importlib, subprocess

log = logging.getLogger("install")

def ensure_cron_job_exists(script_path: str):
    """Zajistí existenci cron úlohy pro spuštění skriptu"""

    # Nastavení cesty k vašemu skriptu, případně upravte podle potřeby
    command = f"python {script_path}"

    # Přístup k crontabu roota; pro běžného uživatele použijte CronTab() bez argumentů
    cron = CronTab(user='root')

    # Vyhledání, zda již úloha existuje
    job_exists = False
    for job in cron:
        if job.command == command:
            job_exists = True
            break

    # Pokud úloha neexistuje, vytvoříme novou
    if not job_exists:
        job1 = cron.new(command=command, comment='My run.py job')
        job1.setall('1 0,12 * * *')  # Nastavení na spuštění v 0:01 a 12:00 každý den
        cron.write()
        log.info("Cron úloha byla vytvořena.")
    else:
        log.info("Cron úloha již existuje.")


def check_and_deactivate_existing_rotation(config_path: str):
    """Zkontroluje a deaktivuje existující rotaci logů"""

    # Kontrola, zda existuje samostatný konfigurační soubor pro rotaci
    if os.path.exists(config_path):
        # Pokud ano, přejmenujeme ho na ".bak" k deaktivaci
        backup_path = config_path + ".bak"
        shutil.move(config_path, backup_path)
        log.info(f"Konfigurace pro rotaci byla deaktivována přejmenováním na {backup_path}")
    else:
        # Kontrola globálního konfiguračního souboru (příklad)
        global_config_path = '/etc/logrotate.conf'
        if os.path.exists(global_config_path):
            with open(global_config_path, 'r') as file:
                lines = file.readlines()
            
            # Příznak pro detekci, zda jsme v sekci pro /var/log/mail.log
            in_section = False
            for i, line in enumerate(lines):
                if line.startswith('/var/log/mail.log'):
                    in_section = True
                if in_section and line.startswith('}'):
                    in_section = False
                    lines[i] = '# ' + line  # Zakomentování zavírací závorky sekce
                if in_section:
                    lines[i] = '# ' + line  # Zakomentování celé sekce
            
            # Zapsání upraveného obsahu zpět do souboru
            with open(global_config_path, 'w') as file:
                file.writelines(lines)
            log.info(f"Konfigurace pro rotaci /var/log/mail.log byla deaktivována zakomentováním v {global_config_path}")

def create_logrotate_symlink(source_file_path, symlink_name):
    """Vytvoří symbolický odkaz pro rotaci logů pomocí logrotate"""

    # Příklad použití
    # source_file_path = '/cesta/k/vašemu/konfiguračnímu/souboru.logrotate'
    # symlink_name = 'název_vaší_aplikace.logrotate'

    # Cílová cesta pro symlink ve složce /etc/logrotate.d/
    target_path = os.path.join('/etc/logrotate.d/', symlink_name)

    # Kontrola, zda symlink již existuje
    if not os.path.islink(target_path):
        # Kontrola, zda cílový soubor existuje (pokud je potřeba)
        if os.path.exists(target_path):
            log.info(f"Symbolický odkaz nebyl vytvořen, protože soubor již existuje na cílové cestě: {target_path}")
        else:
            try:
                # Vytvoření symlinku
                os.symlink(source_file_path, target_path)
                log.info(f"Symbolický odkaz byl úspěšně vytvořen: {target_path} -> {source_file_path}")
            except OSError as e:
                log.error(f"Nepodařilo se vytvořit symbolický odkaz: {e}")

    else:
        log.info(f"Symbolický odkaz již existuje: {target_path}")


def check_modules()->bool:
    """Zkontroluje dostupnost modulů v Pythonu"""
    module_names=['crontab'],
    ok=True
    for module_name in module_names:
        try:
            importlib.import_module(module_name)
            log.info(f"Modul '{module_name}' je dostupný.")
        except ImportError:
            log.error(f"Modul '{module_name}' není dostupný.")
            ok=False
    return ok

def is_package_installed(package_name='pflogsumm'):
    """Zkontroluje, zda je balíček nainstalovaný v systému"""
    try:
        # Spuštění dpkg a hledání balíčku
        output = subprocess.check_output(["dpkg", "-l"], universal_newlines=True)
        if package_name in output:
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        # dpkg skončilo s chybou, pravděpodobně balíček není nainstalovaný
        return False
    

def app_install()->bool:
    print("Spouštění funkce app_install()")
    # Sem přijde logika pro instalaci

def app_check()->bool:
    print("Spouštění funkce app_check()")
    # Sem přijde logika pro kontrolu