#!/bin/bash

# Название виртуального окружения
VENV_DIR="venv"

# Проверка наличия виртуального окружения
if [ ! -d "$VENV_DIR" ]; then
    echo "Виртуальное окружение не найдено. Создание..."
    python3 -m venv "$VENV_DIR"
else
    echo "Виртуальное окружение найдено."
fi

# Активация виртуального окружения
source "$VENV_DIR/bin/activate"

# Установка зависимостей из requirements.txt, если они не установлены
if [ -f "requirements.txt" ]; then
    echo "Установка зависимостей из requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "Файл requirements.txt не найден."
fi
