#!/bin/bash

clear

# folder to store in, no trailing slash
SAVETO=~/radio_files

# the default format of the recorded streams
FORMAT=wav

# set recorder "vlc" "streamripper" "mplayer" or comment out to prompt user for selection
RECORDER=streamripper


#STREAM=http://www.radiosimba.ug:8000/stream
STREAM="http://www.radiosimba.ug:8000/stream -u Mozilla/5.0"

#DATETIME=`date -d '+3 hour' '+%F_T%H.%M.%S'`
DATETIME=`date +'%F_T%H.%M.%S'`
STARTTIME='20:50'
DATE=`date +"%Y-%m-%d"`
STOPTIME='20:53'

#hh:mm YYYY-MM-DD

STREAMNAME='97.0'
FILENAME=$STREAMNAME-$DATETIME.$FORMAT

# create recording command
RECCMD="streamripper $STREAM -d $SAVETO/ -a $FILENAME -s -A"
#RECCMD="cvlc --sout \"#transcode{vcodec=none,acodec=$FORMAT,ab=128,channels=2,samplerate=44100}:std{access=file,mux=$FORMAT,dst=$SAVETO/$FILENAME}\" $STREAM"

# this will stop the recording
STOPCMD="sleep 100; pkill $RECORDER;"


# create the save directory if it doesn't exist
if [ ! -d $SAVETO ]; then
   mkdir $SAVETO
fi

#mkdir -p Simba
# write log file
echo "*** Start $DATE_TIME ***" >> $SAVETO/log.txt

# execute the recording command
echo $RECCMD
# schedule the recording command with time format hh:mm YYYY-MM-DD
echo $RECCMD | at $STARTTIME $DATE

# the kill process for the same time which will sleep for the duration of the show
echo $STOPCMD | at $STOPTIME $DATE

# write log file
echo $RECCMD >> $SAVETO/log.txt
echo $STOPCMD >> $SAVETO/log.txt
