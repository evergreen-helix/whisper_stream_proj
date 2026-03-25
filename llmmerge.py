import ollama
from pydantic import BaseModel
import time
#from llama_cpp import Llama

class merged_response(BaseModel):
  merged_output: str 


class LLMMergeStrategy:
    def __init__(self, model, context_words = 10):
        self.model = model
        self.context_words = context_words

        
    def merge(self, existing_text, new_text, match_info):
        start_time = time.time()
        print(f"Starting LLM Merge at System Time {start_time}")
        if not existing_text:
            return new_text
        
        context_fragment = " ".join(existing_text.split()[-self.context_words:])
        
        #llm_message = '''Here are the two transcript fragments
        #1: ''' + context_fragment + '''
        #2: ''' + new_text


        llm_message = "[FRAGMENT 1]\n" + context_fragment + " \n\n" + "[FRAGMENT 2]\n" + new_text

        


        response = self.model.create_chat_completion(messages=[
                                                {
                                                    "role": "system",
                                                    "content": (
                                                        "You are a transcript stitcher. You receive two overlapping transcript "
                                                        "fragments. Output ONLY the merged text. No commentary, no explanation, "
                                                        "no preamble. Raw merged text only."
                                                    )
                                                },
                                                {
                                                    "role": "user",
                                                    "content": llm_message
                                                }
                                            ],
                                            max_tokens=100,
                                            temperature=0.1
                                        )
                              
                              
                              
                              
    
        output_text = existing_text[:-len(context_fragment)] + " " + response["choices"][0]["message"]["content"]
        
        print(f"Ending LLM Merge that started at System Time {start_time}")
        return output_text