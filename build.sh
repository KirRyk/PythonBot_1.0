#!/usr/bin/env bash
# Выход при ошибке
set -o errexit

STORAGE_DIR=/opt/render/project/.render

# 1. Скачиваем и устанавливаем Google Chrome
if [[ ! -d $STORAGE_DIR/chrome ]]; then
  echo "Скачиваю Chrome..."
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
  rm ./google-chrome-stable_current_amd64.deb
else
  echo "Использую Chrome из кэша"
fi
# 2. Скачиваем и устанавливаем ChromeDriver
# Получаем актуальную версию драйвера, совместимую с установленным Chrome
CHROMEDRIVER_VERSION=$(curl -sS "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE")
if [[ ! -d $STORAGE_DIR/chromedriver ]]; then
  echo "Скачиваю ChromeDriver..."
  mkdir -p $STORAGE_DIR/chromedriver
  cd $STORAGE_DIR/chromedriver
  wget -P ./ "https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip"
  unzip chromedriver-linux64.zip
  # Драйвер находится во вложенной папке после распаковки
  mv ./chromedriver-linux64/chromedriver ./chromedriver
  chmod +x ./chromedriver # Делаем файл исполняемым
  rm -rf ./chromedriver-linux64.zip ./chromedriver-linux64
else
  echo "Использую ChromeDriver из кэша"
fi
# 3. Добавляем пути в переменную PATH (опционально, можно указывать пути явно в коде Python)
export PATH="${PATH}:${STORAGE_DIR}/chrome/opt/google/chrome"
export PATH="${PATH}:${STORAGE_DIR}/chromedriver"