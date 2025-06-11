#!/usr/bin/env python3.7

import os
import logging

# Konfigurační proměnné
ver:str="1.0.0.0"
run_dir = os.path.dirname(os.path.abspath(__file__))
# log_file = '/var/log/pflogsum_mail.log'
log_file = os.path.join(run_dir, 'run.log')

logging.basicConfig(filename=log_file, filemode='a', level=logging.INFO,
                    format='%(asctime)s | %(name)-10s:%(lineno)-06d | %(levelname)-8s : %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

log = logging.getLogger("run")
log.info("-"*20+"\n\n")
log.info("↓"*20)
log.info(" START ".center(20, '*'))
log.info((" v"+ver+" ").center(20, '*'))
log.info("*"*20 + "\n\n")

import sys

def is_venv():
    return (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )

if not is_venv():
    print("Nejsi ve virtuálním prostředí")
    sys.exit(1)

# Zajištění spuštění jako root
# check_root_user()

# Zajištění jediného běhu aplikace
lock_file_path = "/tmp/jb_mailpflogsum_apps.lock"
import fcntl
try:
    lock_file = open(lock_file_path, 'w')
    fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    print("App running in another instance - exiting")
    sys.exit(1)


# BOF *********************
import argparse
import lib.spol as spol
spol.run_dir=run_dir
spol.touch_file_path = os.path.join(run_dir, 'logrotate_cfg', 'maillog_rotate.touch')
from lib.JBConfigParser import JBConfigParser

# ********************************** KONFIG *******************************
log.info("Načítám konfig")
spol.cfg=JBConfigParser(os.path.join(run_dir, 'run.ini'))
log.info("- cfg: init Main sekce")
spol.cfgMain=spol.cfg.get_section('MAIN',True)

log.info("Init main")

#načti a doinicializuj proměnné
logrotate_conf_path = os.path.join(run_dir,'logrotate_cfg', 'postfix_maillog_rotate.conf')
log.info(f"Logrotate cfg pro mail.log: {logrotate_conf_path}")

# začátek s inicializovaným konfigem a logerem
import lib.main as main
import lib.inst as inst

log.info(">>> Run <<<\n")

# Vytvoření parseru
app_args = argparse.ArgumentParser(description="Správa aplikace.")
app_args.add_argument("action", choices=['install', 'check', 'run'], help="Akce k provedení: 'install', 'check' nebo 'run'.")

# Zpracování argumentů
args = app_args.parse_args()

# Rozhodování na základě argumentů
if args.action == 'install':
    log.info("Instalace aplikace")
    inst.app_install()
elif args.action == 'check':
    log.info("Kontrola požadavků aplikace")
    inst.app_check()
elif args.action == 'run':
    log.info("Spuštění aplikace")
    if __name__ == '__main__':
        rotate = main.should_rotate()
        main.send_email_statistics(rotate)
        # if rotate:
            # main.rotate_logs(logrotate_conf_path)
else:
    log.error("Neznámá akce")

# EOF *********************
log.info("*"*20)
log.info(" END ".center(20,"*"))
log.info("↑"*20+"\n\n")