#!/bin/bash

while true; do
    systemctl status nova-jobs
    if [ $? -ne 0 ]; then
        pkill -f process_submissions.py
        systemctl start nova-jobs
        if [ $? -eq 0 ]; then
            curl 'https://maker.ifttt.com/trigger/richnotice/with/key/bXqU9d_59OZWSgr5HxzA8v?value1=XXK%20Job%20Queue%20Died%20And%20Restarted'
        else
            curl 'https://maker.ifttt.com/trigger/richnotice/with/key/bXqU9d_59OZWSgr5HxzA8v?value1=XXK%20Job%20Queue%20Died'
        fi
    fi
    sleep 60
done
