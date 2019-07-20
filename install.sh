#!/bin/bash

apt-get update
# install sqlite3 and create database
apt-get install sqlite3
mkdir -p /data
cd /data
SQLITE_DB="mydb.db"
SQLITE_DB_ADDR="/data/$SQLITE_DB"
sqlite3 $SQLITE_DB ".databases .quit"

# echo 'export SQLITE_DB="mydb.db"' >> /root/.bashrc
# echo 'export SQLITE_DB_ADDR="$(pwd)/$SQLITE_DB"' >> /root/.bashrc


# install python
cd /
wget https://www.python.org/ftp/python/3.6.0/Python-3.6.0.tar.xz
tar xJf Python-3.6.0.tar.xz
cd Python-3.6.0
./configure
make
make install

# delete
cd ..
rm -rf Python-3.6.0*

# echo 'export alias python=python3' >> /root/.bashrc
# source /root/.bashrc