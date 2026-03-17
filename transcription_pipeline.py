class TranscriptionPipeline:
    def __init__(self, whisper_model, merge_selector):
        self.whisper = whisper_model
        self.merge_selector = merge_selector
        self.transcript_history = ""

    def process_audio(self, audio_window):
        segments, _ = self.whisper.transcribe(
            audio_window.flatten(),
            beam_size = 5)
        return " ".join(segment.text for segment in segments)

    def merge_with_history(self, new_transcript):
        #delegates merging
        self.transcript_history = self.merge_selector.merge(
            self.transcript_history, 
            new_transcript
        )
        return self.transcript_history

    def process_and_merge(self, audio_window):
        transcript = self.process_audio(audio_window)
        self.merge_with_history(transcript)

        return self.transcript_history
        
    