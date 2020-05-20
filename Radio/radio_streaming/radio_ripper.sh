#!/bin/bash

clear

# folder to store in, no trailing slash
SAVETO=~/radio_files

# the default format of the recorded streams
FORMAT=mp3

# set recorder "vlc" "streamripper" "mplayer" or comment out to prompt user for selection
RECORDER=streamripper

declare -a StationArray=("http://uk2.internet-radio.com:8332/live -u Mozilla/5.0" "http://cast3.servcast.net:8044/;stream.mp3?1580996196649 -u Mozilla/5.0" "https://edge.mixlr.com/channel/xbxnh -u Mozilla/5.0" "http://66.55.145.43:7344/;?1581951649385 -u Mozilla/5.0" "http://162.244.80.52:8732/stream/1/' -u Mozilla/5.0" "http://www.radiosimba.ug:8000/stream -u Mozilla/5.0" "http://41.202.239.38:88/broadwave.mp3?src=3&rate=1&ref='' -u Mozilla/5.0" "http://41.202.239.38:88/broadwave.mp3  -u Mozilla/5.0" "http://144.217.203.226:8354/stream/1/ -u Mozilla/5.0" "https://www.radiosapientia.com/live -u Mozilla/5.0" "http://66.55.145.43:7404/;?1582179456214 -u Mozilla/5.0" "http://uk6.internet-radio.com:8358/stream -u Mozilla/5.0" "http://66.55.145.43:7383/stream -u Mozilla/5.0" "http://66.55.145.43:7757/stream -u Mozilla/5.0" "http://162.210.196.217:8112/stream.mp3' -u Mozilla/5.0")


DATETIME=`date -d '+3 hour' '+%F_T%H.%M.%S'`
#For testing the script
#DATETIME=`date +'%F_T%H.%M.%S'`
#STARTTIME='20:50'
#DATE=`date +"%Y-%m-%d"`
#STOPTIME='20:53'

#hh:mm YYYY-MM-DD

#radio_stations=(MBABULE PRIME BUKEDDE BUDDU AKABOOZI SIMBA CBS89 CBS88 BEAT SAPIENSA PEARL SALT DIGIDA METRO RECORD)

#FILENAME=${radio_stations[0]}-$DATETIME.$FORMAT

# create recording command
#RECCMD="streamripper $STREAM -d $SAVETO/ -a $FILENAME -s -A"
#RECCMD="cvlc --sout \"#transcode{vcodec=none,acodec=$FORMAT,ab=128,channels=2,samplerate=44100}:std{access=file,mux=$FORMAT,dst=$SAVETO/$FILENAME}\" $STREAM"

# this will stop the recording
#STOPCMD="sleep 100; pkill $RECORDER;"


# create the save directory if it doesn't exist
if [ ! -d $SAVETO ]; then
   mkdir $SAVETO
fi

#mkdir -p Simba
# write log file
echo "*** Start $DATETIME ***" >> $SAVETO/log.txt



# execute the recording command
for radio_station in ${StationArray[@]}; do
    FILENAME=${radio_station}-$DATETIME.$FORMAT
    RECCMD="streamripper $STREAM -d $SAVETO/ -a $FILENAME -s -A"
    $RECCMD
# schedule the recording command with time format hh:mm YYYY-MM-DD
    #echo $RECCMD | at $STARTTIME $DATE
done

# the kill process for the same time which will sleep for the duration of the show - testing the script
#echo $STOPCMD | at $STOPTIME $DATE

# write log file
echo $RECCMD >> $SAVETO/log.txt
#echo $STOPCMD >> $SAVETO/log.txt

#crontab entry to start the shell script
#0 3 * * * /home/planet-expo/radio_ripper.sh  > /home/planet-expo/radio_ripper.log 2>&1
