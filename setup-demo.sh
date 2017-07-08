#!/bin/bash
# ------------------------------------------------------------------
# Based on Script by Jack Farrant
# This script does the following:
#	* Creates a blank ERP Database
#	* Installs BBOXX Modules
#	* Runs Tests
# 
# ------------------------------------------------------------------

SUBJECT=setup-demo
VERSION=0.1.0
USAGE="Usage: setup-demo.sh -h"

# --- Option processing --------------------------------------------

while getopts ":h:" optname
  do
    case "$optname" in
      "h")
        echo $USAGE
        exit 0;
        ;;
    esac
  done

shift $(($OPTIND - 1))

# -----------------------------------------------------------------

LOCK_FILE=/tmp/${SUBJECT}.lock

if [ -f "$LOCK_FILE" ]; then
echo "Script is already running"
fi

# -----------------------------------------------------------------
trap "rm -f $LOCK_FILE" EXIT
touch $LOCK_FILE 

# -----------------------------------------------------------------
#  SCRIPT LOGIC

err_report() {
    echo "Error on line $1"
    exit 1
}
trap 'err_report $LINENO' ERR
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


#kill off any open instances if exist
PID=`ps -eaf | grep odoo | grep -v grep | awk '{print $2}'`
if [[ "" !=  "$PID" ]]; then
  echo "killing $PID"
  kill -9 $PID
fi

#kill off django
PID=`ps -eaf | grep django | grep -v grep | awk '{print $2}'`
if [[ "" !=  "$PID" ]]; then
  echo "killing $PID"
  kill -9 $PID
fi

source venv/bin/activate

cd odoo10

database="odoo_demo"
username="aiden"
password="odoo"


echo "Drop DB '$database'"
psql template1 -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$database';"  &>/dev/null
dropdb --if-exists $database
echo "Initialize Blank DB '$database'"  >/dev/null
./odoo-bin -d $database #--without-demo=stock,mrp,sale,account,account_accountant,purchase,subscription
echo "Update Base Module"
./odoo-bin -d $database --db_user $username --db_password $password -u base --stop-after-init
echo "Install Other Modules"
./odoo-bin -d $database -i stock,mrp,sale,account,account_accountant,purchase,subscription --stop-after-init
./odoo-bin &

sleep 3

cd ../pulse
rm -f db.sqlite3
python manage.py makemigrations
python manage.py migrate
#python manage.py runserver

python manage.py shell <<ORM   # Start django shell.
import bridge.demo as bd

ORM

#kill off odoo again
PID=`ps -eaf | grep odoo | grep -v grep | awk '{print $2}'`
if [[ "" !=  "$PID" ]]; then
  echo "killing $PID"
  kill -9 $PID
fi

#kill off django again
PID=`ps -eaf | grep django | grep -v grep | awk '{print $2}'`
if [[ "" !=  "$PID" ]]; then
  echo "killing $PID"
  kill -9 $PID
fi


# -----------------------------------------------------------------
