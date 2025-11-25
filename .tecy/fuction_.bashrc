
tecy() {
    if [ -z "$1" ]; then
        echo "Uso: tecy <archivo_entrada>"
        return 1
    fi

    local SCRIPT_PATH="$HOME/.tecy/tecy.py" 
    local VENV_ACTIVATE="$HOME/.tecy/tecy_venv/bin/activate" 

    if [ ! -f "$VENV_ACTIVATE" ]; then
        echo "Error: El archivo de activación NO se encontró en $HOME/.tecy/tecy_venv/"
        echo "Asegúrese de que el venv exista y se haya creado con: python3 -m venv $HOME/.tecy/tecy_venv"
        return 1
    fi

    source "$VENV_ACTIVATE" 2>/dev/null

    python3 "$SCRIPT_PATH" "$@"

    deactivate
}
