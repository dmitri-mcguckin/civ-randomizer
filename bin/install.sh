#!/bin/bash

PY_BIN=python3
PY_PATH=$(command -v $PY_BIN)

UPERM_BIN=uperm
UPERM_PATH=$(command -v $UPERM_BIN)

INSTALL_PATH=/opt/civ-bot

#
# 1: Message tag mode:
#   - 1 Say with info tag
#   - 2 Say with error tag
#   - 3 Say with warning tag
#
function say(){
    MODE=""

    if   [[ $1 == 1 ]]; then
        MODE="INFO"
    elif [[ $1 == 2 ]]; then
        MODE="ERROR"
    elif [[ $1 == 3 ]]; then
        MODE="WARN"
    fi

    echo -e "[$MODE]: $2"
}

function dependency() {
  if [[ -z $1 ]]; then
    say 2 "$2 is not installed!\n\tPlease install it before installing civ-bot!"
    exit 0
  else
    say 1 "$2 was found in: $1"
  fi
}

if [[ $USER != "root" ]]; then
  say 2 "Must run the installer as root!"
  exit 0
fi

dependency $PY_PATH $PY_BIN
dependency $UPERM_PATH $UPERM_BIN

if [[ -d $INSTALL_PATH ]]; then
  say 3 "civ-bot was already installed!\n\tOverwriting..."
  rm -rf $INSTALL_PATH
else
  say 1 "Starting a fresh install of civ-bot!"
fi

cd ../
mkdir -p $INSTALL_PATH/bin
mkdir -p $INSTALL_PATH/src
mkdir -p $INSTALL_PATH/config

cp -r ./bin $INSTALL_PATH
cp -r ./src/*.py $INSTALL_PATH/src
cp -r ./res/* $INSTALL_PATH/config

ln -f -s $INSTALL_PATH/bin/civ-bot.sh /usr/bin/civ-bot
ln -f -s $INSTALL_PATH/bin/choose.sh /usr/bin/civ-choose

cp $INSTALL_PATH/config/defaults.json $INSTALL_PATH/config/profile.json

uperm -u root -g root -d $INSTALL_PATH -p 777 -r -y -s
