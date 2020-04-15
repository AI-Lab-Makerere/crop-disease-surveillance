from random import randint
import matplotlib.pyplot as plt

from IPython.display import Audio

class GeneratorClass():

  def __init__(self, main_speech_sample, main_spectogram_sample, Xtrain, sr, sample_length, word_dict_train):
    self.window_sizes = [i for i in range(1,11, 2)]
    self.window_counts = [0 for i in range(1,11, 2) ]
    self.window_movements = [1, 1, 2, 5, 5]
    self.main_speech_sample = main_speech_sample
    self.main_spectogram_sample = main_spectogram_sample
    self.maximum_sample_number = self.main_speech_sample.shape[0]
    self.Xtrain = Xtrain
    self.sr = sr
    self.sample_length = sample_length
    self.word_dict_train = word_dict_train
    self.hit_list = None
    self.predictions = None

  def __iter__(self):

    for window_size_idx in range(len(self.window_sizes)):

      done = False
      current_window_position = 0
      window_size = self.window_sizes[window_size_idx]
      window_movement = self.window_movements[window_size_idx]
      while not done:
        #sample_to_append = None
        if (current_window_position + window_movement + window_size) > self.maximum_sample_number:
          #print (current_window_position + window_movement + window_size)
          #print(maximum_sample_number)
          try:
            padded_sample = np.pad(self.main_spectogram_sample[: , current_window_position + window_movement:],# , :], 
                                  [(0, 0), 
                                    (0,(current_window_position + window_movement + window_size) - self.maximum_sample_number )#,
                                    #(0,0)
                                    ], 
                                  mode='constant', 
                                  constant_values=0)
          except:
            continue
          #yield padded_sample
          self.window_counts[window_size_idx] += 1
          yield make_image_oneshot_task(padded_sample, self.Xtrain)
          done = True 
          
        else:
          #import pdb; pdb.set_trace()
          sample_to_yield = self.main_spectogram_sample[:, current_window_position: current_window_position + window_size]#, :]
          #yield sample_to_yield
          self.window_counts[window_size_idx] += 1
          yield make_image_oneshot_task(sample_to_yield, self.Xtrain)
          #list_of_cut_up_lists[window_size_idx].append(sample_to_append)
          current_window_position += window_movement

  def generate_predictions(self, model, steps_to_predict_from_generator):

    if steps_to_predict_from_generator == "whole_segment":
      steps_to_predict_from_generator = self.sample_length/self.sr/10 #because 10ms

    bbg = self.__iter__()
    self.predictions = model.predict_generator(bbg, steps_to_predict_from_generator, verbose=1)

  
  def find_maximum_N_top_values(self, threshold, N = 1):


    self.hit_list = []
    
    inv_word_dict_train = {v: k for k, v in word_dict_train.items()}

    key_word_count = len(Xtrain)
    #replace 165 with len(Xtrain)
    total_count = 0
    for count in self.window_sizes:
      total_count += count


    for counter in range(total_count):
      print("Counter Value: " + str(counter))
      arr_max_index = np.argmax(self.predictions[( counter*key_word_count ):( (counter+1)*key_word_count )], axis=0)
      print("Arr max index: " + str(arr_max_index))
      print("Hit index: " + str(counter*key_word_count + arr_max_index) )
      print("Hit Value: " + str(self.predictions[counter*key_word_count + arr_max_index]) ) 
      print("Hit Random Assurance: " + str(self.predictions[counter*key_word_count + randint(0,164)]))
      if self.predictions[( counter*key_word_count + arr_max_index)] > threshold:
        #We have a hit
        self.hit_list.append( [ counter, inv_word_dict_train[arr_max_index[0]] ] )

  
  def prediction_index2spectogram_and_speech_index(self, index):
    
    #for hit_idx, word_to_predict in self.hit_list:

    increasing_edge = 0
    increasing_edge_prev = 0
    for edge_of_group_idx, edge_of_group in enumerate(self.window_counts):
      increasing_edge += edge_of_group
      if index < increasing_edge:
        window_size = self.window_sizes[edge_of_group_idx]
        window_movement = self.window_movements[edge_of_group_idx]
        spectogram_idx = index - increasing_edge_prev
        speech_idx = spectogram_idx*10*self.sr
        return (
                  spectogram_idx, #spectogram in
                  speech_idx  
                )
      
      increasing_edge_prev = increasing_edge
        

  def _inspect_speech(self, speech_idx, keyword):

    # Here we find the locations of predictions, the function that maps spectogram to prediction is
    # the segmenting function, so
    # (total_count_of_spectogram/length_of_sample) * segment_start%legnth_of_sample 
    # I am unsure about overlap
    # but let's try anyways
    # The function that maps us back is even simpler. 
    # We take location of prediction, and find in which range of 
    # values it is using the counts list and then we use (location-1) to account for 0 start
    # of array + list counts. 


      speech_sample_to_display = self.main_speech_sample[speech_idx:speech_idx + self.sr ]

      speech_sample_to_display = butter_bandpass_filter(speech_sample_to_display, lowcut, highcut, rate, order=1)
      # Only use a short clip for our demo
      if np.shape(speech_sample_to_display)[0] / float(rate) > 10:
          speech_sample_to_display = speech_sample_to_display[0 : rate * 10]
      print("Length in time (s): ", np.shape(speech_sample_to_display)[0] / float(rate))
      print("Keyword Found: ", keyword)
      # Play the audio

      return speech_sample_to_display


  def _inspect_spectogram(self, spectogram_idx):

      spectogram_sample_to_display = self.main_spectogram_sample[:, spectogram_idx:spectogram_idx + self.window_sizes[-1]]

      n_fft = int(self.sr * 0.2) #20ms windows
      hop_length = int(n_fft // 2) #In case of remainders will this cause a slow drift over time ????

      librosa.display.specshow(spectogram_sample_to_display, sr=self.sr, hop_length=hop_length, 
                         x_axis='time', y_axis='mel');
      plt.colorbar(format='%+2.0f dB');


  def inspect_predictions(self, prediction_to_inspect):

    #self.window_sizes = [i for i in range(1,11, 2)]
    #self.window_counts = [0 for i in range(1,11, 2) ]
    #self.window_movements = [1, 1, 2, 5, 5]


    idx, keyword = prediction_to_inspect
    spectogram_idx, speech_idx = self.prediction_index2spectogram_and_speech_index(idx)

    self._inspect_spectogram(spectogram_idx)
    speech_sample = self._inspect_speech(speech_idx, keyword)

    return speech_sample


## Does this belong here??
def big_bad_generator_for_one_shot_tasks_from_cut_ups(main_speech_sample, Xtrain, Categories):
  window_beginning = 0
  window_sizes = [i for i in range(1,11, 2)]
  window_counts = [0 for i in range(1,11, 2) ]
  # if time allows I should just make window movements the minimum or a small 
  # number for most size values
  window_movements = [1, 1, 2, 5, 5]
  #main_speech_sample = resize_and_color_image(main_speech_sample)
  print(main_speech_sample.shape)
  assert len(window_sizes) == len(window_movements)
  maximum_sample_number = main_speech_sample.shape[1]

  for window_size_idx in Qrange(len(window_sizes)):

    done = False
    current_window_position = 0
    window_size = window_sizes[window_size_idx]
    window_movement = window_movements[window_size_idx]
    while not done:
      #sample_to_append = None
      if (current_window_position + window_movement + window_size) > maximum_sample_number:
        #print (current_window_position + window_movement + window_size)
        #print(maximum_sample_number)
        try:
          padded_sample = np.pad(main_speech_sample[: , current_window_position + window_movement:],# , :], 
                                [(0, 0), 
                                  (0,(current_window_position + window_movement + window_size) - maximum_sample_number )#,
                                  #(0,0)
                                  ], 
                                mode='constant', 
                                 constant_values=0)
        except:
          continue
        #yield padded_sample
        window_counts[window_size_idx] += 1
        yield make_image_oneshot_task(padded_sample, Xtrain, Categories)
        done = True 
         
      else:
        sample_to_yield = main_speech_sample[:, current_window_position: current_window_position + window_size]#, :]
        #yield sample_to_yield
        window_counts[window_size_idx] += 1
        yield make_image_oneshot_task(sample_to_yield, Xtrain, Categories)
        #list_of_cut_up_lists[window_size_idx].append(sample_to_append)
        current_window_position += window_movement



