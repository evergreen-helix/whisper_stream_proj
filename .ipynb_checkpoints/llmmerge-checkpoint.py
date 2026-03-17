import ollama
from pydantic import BaseModel
import time

class merged_response(BaseModel):
  merged_output: str 


class LLMMergeStrategy:
    def __init__(self, model_name, context_words = 10):
        self.model_name = model_name
        self.context_words = context_words

        
    def merge(self, existing_text, new_text, match_info):
        start_time = time.time()
        print(f"Starting LLM Merge at System Time {start_time}")
        if not existing_text:
            return new_text
        
        context_fragment = " ".join(existing_text.split()[-self.context_words:])
        
        llm_message = '''Here are the two transcript fragments
        1: ''' + context_fragment + '''
        2: ''' + new_text


        
        response = ollama.chat(model=self.model_name, format = merged_response.model_json_schema(), messages=[
                {'role': 'system', 'content': '''You merge overlapping transcript fragments. The end of transcript 1 overlaps with the start of transcript 2. Remove the duplication and return ONLY the merged text.
                
                Rules:
                - Output ONLY the merged text
                - No explanations, notes, or commentary
                - If there is no clear overlap, return transcript 2 unchanged
                
                Example:
                1: The cat sat on the mat
                2: on the mat and then fell asleep
                Output: The cat sat on the mat and then fell asleep'''}
                ,
                {'role': 'user', 'content': llm_message}
            ])
    
        output_text = existing_text[:-len(context_fragment)] + " " + merged_response.model_validate_json(response.message.content).merged_output
        
        print(f"Ending LLM Merge that started at System Time {start_time}")
        return output_text