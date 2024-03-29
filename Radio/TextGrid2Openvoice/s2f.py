import argparse
import csv
import os   
from pydub import AudioSegment
from parse_textgrid import remove_empty_lines, TextGrid

#FIXME the segments overwrite each other - add a file specific prefix
#FIXME the segments crowd the other files and confuse the scripts - create a directory for the segment files and ignore it
#FIXME create a new csv file then append all segments to it..

parser = argparse.ArgumentParser(description='Convert segments to common voice format files')
parser.add_argument('input_dir')
#parser.add_argument('input_annotation')
#parser.add_argument('--output-audio-path', default='/home/sha3bola/repos/rcrops/segment_to_file_util/')
#parser.add_argument('--output-csv-path', default='/home/sha3bola/repos/rcrops/segment_to_file_util/')
parser.add_argument('--output-prefix', default='seg')

args = parser.parse_args()
files_in_dir = os.listdir(args.input_dir)


if not os.path.exists(args.input_dir + "/clips/"):
    os.mkdir(args.input_dir + "/clips")


if not os.path.exists(args.input_dir + "/JUNK_clips/"):
    os.mkdir(args.input_dir + "/JUNK_clips")

if not os.path.exists(args.input_dir + "/MUSIC_clips/"):
    os.mkdir(args.input_dir + "/MUSIC_clips")

if not os.path.exists(args.input_dir + "/PHONE_clips/"):
    os.mkdir(args.input_dir + "/PHONE_clips")

if not os.path.exists(args.input_dir + "/INCOMPLETE_clips/"):
    os.mkdir(args.input_dir + "/INCOMPLETE_clips")

if not os.path.exists(args.input_dir + "/OVERLAPPING_clips/"):
    os.mkdir(args.input_dir + "/OVERLAPPING_clips")



if os.path.exists(args.input_dir + "/" + "index" + ".csv"):
    os.remove(args.input_dir + "/" + "index" + ".csv")

if os.path.exists(args.input_dir + "/" + "junk" + ".csv"):
    os.remove(args.input_dir + "/" + "junk" + ".csv")

if os.path.exists(args.input_dir + "/" + "music" + ".csv"):
    os.remove(args.input_dir + "/" + "music" + ".csv")

if os.path.exists(args.input_dir + "/" + "phone" + ".csv"):
    os.remove(args.input_dir + "/" + "phone" + ".csv")

if os.path.exists(args.input_dir + "/" + "incomplete" + ".csv"):
    os.remove(args.input_dir + "/" + "incomplete" + ".csv")

if os.path.exists(args.input_dir + "/" + "overlapping" + ".csv"):
    os.remove(args.input_dir + "/" + "overlapping" + ".csv")


for file_in_dir in files_in_dir:

    if file_in_dir in ["clips", "JUNK_clips", "MUSIC_clips", "PHONE_clips", "INCOMPLETE_clips", "OVERLAPPING_clips"]:
        continue        

    if file_in_dir.split(".")[1] not in ["ogg", "mp3", "wav"]:
        continue

    audio_file_path = os.path.join(args.input_dir, file_in_dir)
    annotation_file_path = os.path.join(args.input_dir, file_in_dir.split(".")[0] + ".TextGrid")
    #print(audio_file_path.split(".")[-1])
    try:    
        if audio_file_path.split(".")[-1] == "mp3":
            main_audio_file = AudioSegment.from_mp3(audio_file_path)
        elif audio_file_path.split(".")[-1] == "wav":
            main_audio_file = AudioSegment.from_wav(audio_file_path)
        elif audio_file_path.split(".")[-1] == "ogg":
            main_audio_file = AudioSegment.from_ogg(audio_file_path)
    except:
        err_fd =  open("errors.txt", "a+")
        err_fd.write(annotation_file_path)
        err_fd.close()        
        continue
    
    try:     
        f = open(annotation_file_path, "rb")
        text = f.readlines()
        text = remove_empty_lines(text)
        main_annotation_file = TextGrid(text)
        f.close()

    except:
        err_fd = open("errors.txt", "a+")
        err_fd.write(annotation_file_path)
        err_fd.close()        
        continue
            
        
    number_of_items = len(main_annotation_file.tier_list[0]['items'])
    segment_files_list = [] #(file_path, text)
    for i in range(number_of_items):
        
        segment_to_seperate = main_annotation_file.tier_list[0]['items'][i]
        segment_xmin = float(segment_to_seperate["xmin"]) * 1000
        segment_xmax = float(segment_to_seperate["xmax"]) * 1000
        total_segment_duration = segment_xmax - segment_xmin
        #print(type(segment_xmin))
        #print(segment_xmin)
        #print(type(segment_xmax))
        #print(segment_xmax)
        segment_audio = main_audio_file[segment_xmin:segment_xmax]
        segment_text = segment_to_seperate["text"]

        if segment_text.lower() == "junk." or segment_text.lower() == "junk":
            segment_audio_path =  audio_file_path.split(".")[0].split("/")[-1]  + args.output_prefix + str(i) + ".mp3"
            segment_audio = segment_audio.set_channels(1)
            segment_audio.export(args.input_dir + "/" + "JUNK_clips" + "/" + segment_audio_path ,format="mp3")        

        elif segment_text.lower() == "music." or segment_text.lower() == "music":
            segment_audio_path =  audio_file_path.split(".")[0].split("/")[-1]  + args.output_prefix + str(i) + ".mp3"
            segment_audio = segment_audio.set_channels(1)
            segment_audio.export(args.input_dir + "/" + "MUSIC_clips" + "/" + segment_audio_path ,format="mp3")        

        elif segment_text.lower() == "phone call." or segment_text.lower() == "phone call" or segment_text.lower() == "phone speech." or segment_text.lower() == "phone speech":
            segment_audio_path =  audio_file_path.split(".")[0].split("/")[-1]  + args.output_prefix + str(i) + ".mp3"
            segment_audio = segment_audio.set_channels(1)
            segment_audio.export(args.input_dir + "/" + "PHONE_clips" + "/" +  segment_audio_path ,format="mp3")        


        elif total_segment_duration >= 30000 or segment_text.lower().rstrip().lstrip() == "":
            pass

        elif segment_text.lower() == "overlap." or segment_text.lower() == "overlapping." or segment_text.lower() == "overlap" or segment_text.lower() == "overlapping":
            segment_audio_path = audio_file_path.split(".")[0].split("/")[-1]  + args.output_prefix + str(i) + ".mp3"
            segment_audio = segment_audio.set_channels(1)
            segment_audio.export(args.input_dir + "/" + "OVERLAPPING_clips" + "/" + segment_audio_path ,format="mp3")

        
        else:
            segment_audio_path = audio_file_path.split(".")[0].split("/")[-1]  + args.output_prefix + str(i) + ".mp3"
            segment_audio = segment_audio.set_channels(1)
            segment_audio.export(args.input_dir + "/" + "clips" + "/" + segment_audio_path ,format="mp3")


        segment_files_list.append( (segment_audio_path, segment_text, total_segment_duration) ) 

    csv_file_path = args.input_dir + "/" + "index" + ".csv"
    #with open(csv_file_path, "a") as csv_fd:
    csv_fd = open(csv_file_path, "a+")
    jk_csv_file_path = args.input_dir + "/" + "junk" + ".csv"
    jk_fd =  open(jk_csv_file_path, "a+")
    music_csv_file_path = args.input_dir + "/" + "music" + ".csv"
    music_fd = open(music_csv_file_path, "a+")
    phone_csv_file_path = args.input_dir + "/" + "phone" + ".csv"
    phone_fd = open(phone_csv_file_path, "a+")
    #incomplete_csv_file_path = args.input_dir + "/" + "incomplete" + ".csv"
    #incomplete_fd = open(incomplete_csv_file_path, "a+")
    overlapping_csv_file_path = args.input_dir + "/" + "overlapping" + ".csv"
    overlapping_fd = open(overlapping_csv_file_path, "a+")
    
    csvwriter = csv.writer(csv_fd,
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    jk_csvwriter = csv.writer(jk_fd,
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    music_csvwriter = csv.writer(music_fd,
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    phone_csvwriter = csv.writer(phone_fd,
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #incomplete_csvwriter = csv.writer(incomplete_fd,
    #                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
    overlapping_csvwriter = csv.writer(overlapping_fd,
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    
    for path, text, duration in segment_files_list:
        if text.lower().strip(" .!") in ["junk"]:
            jk_csvwriter.writerow([str(path), str(text),  str(duration)])
        elif text.lower().strip(" .!") in ["music"]:
            music_csvwriter.writerow([str(path), str(text),  str(duration)])
        elif text.lower().strip(" .!") in ["phone call", "phone speech"]:
            phone_csvwriter.writerow([str(path), str(text),  str(duration)])
        elif total_segment_duration >= 30000 or text.lower().rstrip().lstrip() == "":
            pass
        elif segment_text.lower().strip(" .!") in ["overlap", "overlapping"]:
            overlapping_csvwriter.writerow([str(path), str(text),  str(duration)])
        elif segment_text.lower().strip(" .!") in ["advert", "radio jingle", "phone contact"]:
            pass
        else:
            csvwriter.writerow([str(path), str(text),  str(duration)])





