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


if not os.path.exists(args.input_dir + "/segments/"):
    os.mkdir(args.input_dir + "/segments")

if os.path.exists(args.input_dir + "/" + "index" + ".csv"):
    os.remove(args.input_dir + "/" + "index" + ".csv")

if os.path.exists(args.input_dir + "/" + "junk" + ".csv"):
    os.remove(args.input_dir + "/" + "junk" + ".csv")

for file_in_dir in files_in_dir:

    if file_in_dir in ["segments"]:
        continue        

    if file_in_dir.split(".")[1] not in ["ogg", "mp3", "wav"]:
        continue

    audio_file_path = os.path.join(args.input_dir, file_in_dir)
    annotation_file_path = os.path.join(args.input_dir, file_in_dir.split(".")[0] + ".TextGrid")
    main_audio_file = AudioSegment.from_mp3(audio_file_path)

    with open(annotation_file_path, "rb") as f:
        text = f.readlines()
    text = remove_empty_lines(text)
    main_annotation_file = TextGrid(text)

    number_of_items = len(main_annotation_file.tier_list[0]['items'])
    segment_files_list = [] #(file_path, text)
    for i in range(number_of_items):
        
        segment_to_seperate = main_annotation_file.tier_list[0]['items'][i]
        segment_xmin = float(segment_to_seperate["xmin"]) * 1000
        segment_xmax = float(segment_to_seperate["xmax"]) * 1000
        total_segment_duration = segment_xmax - segment_xmin
        print(type(segment_xmin))
        print(segment_xmin)
        print(type(segment_xmax))
        print(segment_xmax)
        segment_audio = main_audio_file[segment_xmin:segment_xmax]
        segment_audio_path = args.input_dir + "/" + "segments" + "/" + audio_file_path.split(".")[0].split("/")[-1]  + args.output_prefix + str(i) + ".mp3"
        segment_audio.export(segment_audio_path ,format="mp3")
        segment_text = segment_to_seperate["text"]
        segment_files_list.append( (segment_audio_path, segment_text, total_segment_duration) ) 

    csv_file_path = args.input_dir + "/" + "index" + ".csv"
    #with open(csv_file_path, "a") as csv_fd:
    csv_fd = open(csv_file_path, "a")
    jk_csv_file_path = args.input_dir + "/" + "junk" + ".csv"
    jk_fd =  open(jk_csv_file_path, "a")
    csvwriter = csv.writer(csv_fd,
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    jk_csvwriter = csv.writer(jk_fd,
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for path, text, duration in segment_files_list:
        if text == "JUNK":
            jk_csvwriter.writerow([str(path), str(text),  str(duration)])
        else:
            csvwriter.writerow([str(path), str(text),  str(duration)])





