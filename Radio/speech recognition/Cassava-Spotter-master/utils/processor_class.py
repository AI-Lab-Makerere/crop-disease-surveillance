
import os

class DataProcessor():

    def __init__(self, main_data_dir, val_dir = None, test_dir= None, do_train_val_test_split = False):
        self.main_dir = main_data_dir
        self.val_dir = val_dir
        self.test_dir = test_dir        
        #self.convert_ogg2wav()
        #self.generate_dir_spectrograms()


    def convert_ogg2wav():

        self.train_wavfiles = [os.path.join(root, name)
            for root, dirs, files in os.walk(self.main_dir)#"data/nlp_keyword_bucket/train_1/")
            for name in files
            if name.endswith((".wav"))]

        if self.val_dir: 

            self.val_wavfiles = [os.path.join(root, name)
                for root, dirs, files in os.walk(self.val_dir)#"data/nlp_keyword_bucket/val_1/")
                for name in files
                if name.endswith((".wav"))]

        if self.test_dir:

            self.test_wavfiles = [os.path.join(root, name)
                for root, dirs, files in os.walk(self.test_dir)#"data/nlp_keyword_bucket/test_1/")
                for name in files
                if name.endswith((".wav"))]

        for filename in self.train_wavfiles:
            words = re.findall(r"[\w']+", filename)
            os.system("ffmpeg -y -i {0} {0}".format(filename))

        if self.val_dir:

            for filename in self.val_wavfiles:
                words = re.findall(r"[\w']+", filename)
                os.system("ffmpeg -y -i {0} {0}".format(filename))

        if self.test_dir:
            for filename in self.test_wavfiles:
                words = re.findall(r"[\w']+", filename)
                os.system("ffmpeg -y -i {0} {0}".format(filename))


    def generate_dir_spectrograms(self,main_dir, val_dir = None, test_dir = None):

        #train_wavfiles = [os.path.join(root, name)
         #   for root, dirs, files in os.walk(main_dir)#"data/nlp_keyword_bucket/train_1/")
          #  for name in files
           # if name.endswith((".wav"))]

        #if val_dir:

            #val_wavfiles = [os.path.join(root, name)
             #   for root, dirs, files in os.walk(val_dir)#"data/nlp_keyword_bucket/val_1/")
              #  for name in files
               # if name.endswith((".wav"))]
        
        #if test_dir:

         #   test_wavfiles = [os.path.join(root, name)
          #      for root, dirs, files in os.walk(test_dir)#"data/nlp_keyword_bucket/test_1/")
           #     for name in files
           #     if name.endswith((".wav"))]

        for train_wavfl in self.train_wavfiles:
          generate_mel_spectogram(train_wavfl)
          
        if self.val_dir:
            for val_wavfl in self.val_wavfiles:
              generate_mel_spectogram(val_wavfl)
        
        if self.test_dir:
            for test_wavfl in self.test_wavfiles:
              generate_mel_spectogram(test_wavfl)


