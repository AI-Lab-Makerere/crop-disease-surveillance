#!/bin/bash

clear

# folder to store in, no trailing slash
SAVETO=~/radio_files

# the default format of the recorded streams
FORMAT=mp3

# set recorder "vlc" "streamripper" "mplayer" or comment out to prompt user for selection
RECORDER=streamripper


#STREAM=http://www.radiosimba.ug:8000/stream
STREAM=http://www.radiosimba.ug:8000/stream -u Mozilla/5.0 -d

DATETIME=`date -d '+3 hour' '+%F_T%H.%M.%S'`
DATE_TIME=`date +'%F_T%H.%M.%S'`
START_TIME=`10:00`
DATE=`date +"%Y-%m-%d"`
STOP_TIME=`10:10`

#hh:mm YYYY-MM-DD

STREAMNAME='97.0'
FILENAME=$STREAMNAME-$DATETIME.$FORMAT

# create recording command
REC_CMD="$RECORDER $STREAM -d $SAVETO/ -a ${FILENAME// /_} -s -A -l 300"

# this will stop the recording
STOP_CMD="sleep 300; pkill $RECORDER;"


# create the save directory if it doesn't exist
if [ ! -d $SAVETO ]; then
   mkdir $SAVETO
fi

#mkdir -p Simba
# write log file
echo "*** Start $DATE_TIME ***" >> $SAVETO/log.txt

# execute the recording command
echo $REC_CMD
# schedule the recording command with time format hh:mm YYYY-MM-DD
echo $REC_CMD | at $START_TIME $DATE

# the kill process for the same time which will sleep for the duration of the show
echo $STOP_CMD | at $STOP_TIME $DATE

# write log file
echo $REC_CMD >> $SAVETO/log.txt
echo $STOP_CMD >> $SAVETO/log.txt
