import re
import string

from simplemerge import SimpleMergeStrategy
from llmmerge import LLMMergeStrategy

class MergeStrategySelector:
    def __init__(self, context_words = 10):
        self.context_words = context_words
        self.stats = {'exact': 0, 'fuzzy': 0, 'llm': 0}
        self.simple_strategy = SimpleMergeStrategy()
        self.llm_strategy = LLMMergeStrategy(model_name = 'llama3.2:3b', context_words = self.context_words)

    def merge(self, existing_text, new_text):
        
        new_text_clean = re.sub(r'\.{3}(?=\S|$)', '... ', new_text) #this should be somewhere else, tbd
        
        if not existing_text:
            return new_text_clean

        context_text = " ".join(existing_text.split()[-self.context_words:])
        
        match_info = self._analyse_overlap(context_text, new_text_clean, max_match_len = 10)
        
        if match_info['type'] == "exact":
            merged_output = self.simple_strategy.merge(existing_text, new_text_clean, match_info)
            self.stats["exact"] += 1
        elif match_info['type'] == 'llm':
            merged_output = self.llm_strategy.merge(existing_text, new_text_clean, match_info)
            self.stats["llm"] += 1

        return merged_output

    def _analyse_overlap(self, context_text, new_text, max_match_len = 10):

        context_text_analysis = context_text.translate(str.maketrans('', '', string.punctuation)).lower()
        new_text_analysis = new_text.translate(str.maketrans('', '', string.punctuation)).lower()
        
        context_words = context_text_analysis.split()
        new_words = new_text_analysis.split()
        
        match_len_limit = min(len(context_words), len(new_words), max_match_len)
        
        match_index = 0
        for i in range(match_len_limit, 0,- 1):
            v1 = context_words[-i:]
            v2 = new_words[:i]
            if v1 == v2:
                match_index = i
                break
        merge_type = "exact"
        if match_index == 0:
            merge_type = "llm"
            print("DEBUG: Exact Merging Failed")
            print(context_words[-match_len_limit:])
            print(new_words[:match_len_limit])
            
        
        return {'type': merge_type, 'overlap_length': match_index}