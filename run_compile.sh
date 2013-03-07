#! /bin/bash

BIN=bin
SOURCES=`find src -name "*.java"`

if [ ! -d "$BIN" ]; then
  mkdir -p $BIN
fi

javac -cp lib/*:. $SOURCES -d $BIN