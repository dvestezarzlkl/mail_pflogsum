import os
import sys
import subprocess

def check_venv():
    """Ověří, že skript běží ve virtuálním prostředí (venv)."""
    if sys.prefix == sys.base_prefix:
        print("Chyba: Skript musí být spuštěn uvnitř virtuálního prostředí (venv). Ukončuji.")
        sys.exit(1)
    else:
        print(f"Virtuální prostředí aktivní: {sys.prefix}")

def check_sudo()->None:
    """Ověří, zda je skript spuštěn s právy roota (sudo)."""
    if os.geteuid() != 0:
        print("Chyba: Skript není spuštěn s právy roota (sudo). Ukončuji.")
        sys.exit(1)


def check_run_py_file()->None:
    """Zkontroluje, zda v aktuálním adresáři existuje soubor venv_run.py,
       čímž ověří, že jsme ve správném (root) adresáři projektu."""
    file_name = "venv_run.py"
    if not os.path.exists(file_name):
        print(f"Chyba: V aktuálním adresáři ({os.getcwd()}) "
              f"není nalezen soubor '{file_name}'. Ukončuji.")
        sys.exit(1)
        
def run_requirements_install():
    """Spustí pip install -r requirements.txt, pokud soubor existuje."""
    req_file = "requirements.txt"
    if os.path.exists(req_file):
        print(f"Instaluji knihovny z {req_file}...")
        try:
            subprocess.run(["pip", "install", "-r", req_file], check=True)
            print("Knihovny byly úspěšně nainstalovány.")
        except subprocess.CalledProcessError as e:
            print("Chyba při instalaci knihoven přes pip:\n", e)
            sys.exit(1)
    else:
        print(f"Soubor {req_file} neexistuje. Přeskakuji instalaci knihoven.")
        
def check_pflogsum():
    """Zkontroluje, zda je nainstalován pflogsum, a pokud ne, pokusí se jej nainstalovat."""
    try:
        # Ověření, zda je pflogsum dostupný
        subprocess.run(["which", "pflogsum"], check=True, stdout=subprocess.DEVNULL)
        print("Pflogsum je již nainstalován.")
    except subprocess.CalledProcessError:
        print("Pflogsum není nainstalován. Pokouším se jej nainstalovat...")
        try:
            subprocess.run(["apt", "install", "-y", "pflogsum"], check=True)
            print("Pflogsum byl úspěšně nainstalován.")
        except subprocess.CalledProcessError as e:
            print("Chyba při instalaci pflogsum:\n", e)
            sys.exit(1)


def main():
    print("===== Spouštím instalační skript =====")

    # Kontrola sudo
    print(" ---- Kontrola sudo ----")
    check_sudo()

    # Kontrola, že jsme ve virtuálním prostředí
    print(" ---- Kontrola virtuálního prostředí (venv) ----")
    check_venv()

    # Kontrola, že běžíme z root adresáře aplikace (!run.py)
    print(" ---- Kontrola root adresáře aplikace ----")
    check_run_py_file()

    # Spuštění instalačního skriptu rq_try_install_requirements.py
    print(" ---- Instalace Python knihoven z requirements.txt ----")
    run_requirements_install()

    # Kontrola a instalace pflogsum
    print(" ---- Kontrola a instalace pflogsum ----")
    check_pflogsum()

    print("===== Instalační skript dokončen úspěšně. =====")


if __name__ == "__main__":
    main()
