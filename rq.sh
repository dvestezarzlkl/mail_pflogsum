#!/bin/bash

# vygeneruje requirements.txt ze zdrojového kódu
# Vyčisti terminál
clear

# Cesta k root adresáři projektu
PROJECT_PATH=$(dirname "$(realpath "$0")")

# Název souboru logu
LOG_FILE="rq.log"
VENV_DIR="venv310"

# Zkontroluj, zda je nainstalován pipreqs
LOG="\n"

# Detekce aktivního venv
if [[ -z "$VIRTUAL_ENV" ]]; then
    if [[ -d "$VENV_DIR" ]]; then
        LOG+="Virtuální prostředí není aktivní. Pokouším se aktivovat...\n"
        source "$VENV_DIR/bin/activate"
        if [[ -z "$VIRTUAL_ENV" ]]; then
            LOG+="Nepodařilo se aktivovat virtuální prostředí. Ukončuji...\n"
            echo -e "$LOG" > "$LOG_FILE"
            cat "$LOG_FILE"
            exit 1
        else
            LOG+="Virtuální prostředí úspěšně aktivováno.\n"
        fi
    else
        LOG+="Virtuální prostředí ($VENV_DIR) neexistuje. Ukončuji...\n"
        echo -e "$LOG" > "$LOG_FILE"
        cat "$LOG_FILE"
        exit 1
    fi
fi

LOG+="Virtuální prostředí aktivní: $VIRTUAL_ENV\n\n"

if ! command -v pipreqs &> /dev/null; then
    LOG+="pipreqs není nainstalován. Pokouším se jej nainstalovat...\n"
    pip install pipreqs &>> "$LOG_FILE"
    if ! command -v pipreqs &> /dev/null; then
        LOG+="Nepodařilo se nainstalovat pipreqs. Ukončuji...\n"
        echo -e "$LOG" > "$LOG_FILE"
        cat "$LOG_FILE"
        exit 1
    else
        LOG+="pipreqs byl úspěšně nainstalován.\n"
    fi
fi

if ! command -v pipreqs &> /dev/null
then
    LOG+="pipreqs není nainstalován. Prosím, nainstalujte ho pomocí následujícího příkazu:\n"
    LOG+="pip install pipreqs\n"
    echo -e "$LOG" > "$LOG_FILE"
    exit 1
fi

# Zjištění verze Pythonu
PYTHON_VERSION=$(python3 --version 2>&1)

# Použij pipreqs k vygenerování requirements.txt
pipreqs "$PROJECT_PATH" --force --ignore "$VENV_DIR" &>> "$LOG_FILE"

# Vytvoření logu do proměnné LOG
if [ -f "$PROJECT_PATH/requirements.txt" ]; then
    LOG+="Non-standard, non-project libraries used in the project (pro verzi $PYTHON_VERSION):\n"
    while IFS= read -r line; do
        LOG+="- $line\n"
    done < "$PROJECT_PATH/requirements.txt"
    LOG+="\nChybějící knihovny lze doinstalovat pomocí následujícího příkazu:\n"
    LOG+="> pip install -r requirements.txt\n"
else
    LOG+="Chyba: Nepodařilo se vygenerovat requirements.txt\n"
fi

# Zápis obsahu logu do souboru a jeho zobrazení
LOG+="\n"
echo -e "$LOG" > "$LOG_FILE"
cat "$LOG_FILE"
