import argparse
import pandas
from random import choice, randint
parser = argparse.ArgumentParser(description='Convert segments to common voice format files')
parser.add_argument('input_path')
parser.add_argument('output_path')
#parser.add_argument('input_annotation')
#parser.add_argument('--output-audio-path', default='/home/sha3bola/repos/rcrops/segment_to_file_util/')
#parser.add_argument('--output-csv-path', default='/home/sha3bola/repos/rcrops/segment_to_file_util/')
parser.add_argument('--output-prefix', default='seg')

args = parser.parse_args()
csv_file_path = args.input_path

csv_df = pandas.read_csv(csv_file_path, quotechar="|", names=["Path", "Transcript", "Time - milliseconds"])

number_of_segments = len(csv_df["Transcript"])

positive_examples = []
negative_examples = []
for trans in csv_df["Transcript"]:
    word_list = trans.lower().rstrip(" .?!").lstrip().split(" ")
    positive_example = choice(word_list)
    while True:
        segment_number = randint(0,number_of_segments - 1)
        negative_example = csv_df["Transcript"][segment_number]
        negative_example = negative_example.lower().rstrip(" .?!").lstrip().split(" ")
        negative_example = choice(negative_example)
        if negative_example not in word_list:
            break
    print(positive_example)
    print(negative_example)
    print("_______________")
    positive_examples.append(positive_example)
    negative_examples.append(negative_example)
csv_df["Positive Example"] = positive_examples
csv_df["Negative Example"] = negative_examples

csv_df.to_csv(args.output_path)



