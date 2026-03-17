import numpy as np

class AudioBuffer:
    def __init__(self, window_size = 5, overlap_size = 2, sample_rate = 16000,  model_vad = None, utils = None):
        self.window_size = window_size
        self.overlap_size = overlap_size
        self.sample_rate = sample_rate
        self.audio_data_buffer = np.array([], dtype = np.float32)
        self.window_size_samp = self.window_size * self.sample_rate
        self.overlap_size_samp = self.overlap_size * self.sample_rate
        self.model_vad = model_vad
        self.utils = utils
        
    def append_chunk(self, audio_data):
        self.audio_data_buffer = np.append(self.audio_data_buffer, audio_data.copy())
        
    def get_buffer_size(self):
        return len(self.audio_data_buffer)

    def get_speech_samplestamps(self, analysis_audio):
        
        (get_speech_timestamps, _, _, _, _) = self.utils
        
        speech_samplestamps = get_speech_timestamps(
                  audio = analysis_audio,
                  model = self.model_vad,
                  return_seconds= False,
                  min_speech_duration_ms = 5, 
                  min_silence_duration_ms = 5
            )

        return [[seg['start'], seg['end']] for seg in speech_samplestamps]

    def get_silence_samplestamps(self, analysis_audio):

        speech_samplestamps = self.get_speech_samplestamps(analysis_audio)

        audio_length = len(analysis_audio)

        start = 0
        end = audio_length
        silence_list = []
        
        for seg in speech_samplestamps:
            if start == seg[0]:
                start = seg[1] + 1
                continue
            silence_list.append([start,seg[0] -  1])
            start = seg[1] + 1
        if start < end:
            silence_list.append([start, end])

        return silence_list

    def _get_overlaps(self, zone_1, zone_list_2):
        zones_out = []
        for zone_2 in zone_list_2:
            if zone_2[0] <= zone_1[1] and zone_1[0] <= zone_2[1]:
                zones_out.append([max(zone_1[0], zone_2[0]), min(zone_1[1], zone_2[1])])
        
        return zones_out

    def _get_best_cuts(zone_list):
        return [entry[1] for entry in sorted([[zone[1] - zone[0], (zone[1]+zone[0]) // 2] for zone in zone_list], key = lambda x : x[0], reverse = True)]
        
    
    def _find_cut_points(self, analysis_audio):
        
        speech_data = self.get_speech_samplestamps(analysis_audio)
        
        def calc_sil_len(x):
            x['len'] = x['end'] - x['start']
            return x

        silence_data = [calc_sil_len(x) for x in silence_data]

        def diff_to_cut(x):
            cut_1_target = self.window_size_samp - self.overlap_size_samp
            cut_2_target = self.window_size_samp

            x['c1_diff'] = abs(cut_1_target - x['start'])
            x['c2_diff'] = abs(cut_2_target - x['end'])
            return x

        silence_data = [diff_to_cut(x) for x in silence_data]
        print(silence_data)
        
        return silence_data
            
    def get_window(self):
        # return concatenated window if ready, else None
        if len(self.audio_data_buffer) >= self.window_size_samp:
            window = self.audio_data_buffer[:self.window_size_samp]
            self.audio_data_buffer = self.audio_data_buffer[(self.window_size_samp - self.overlap_size_samp):]
            return window
        return None