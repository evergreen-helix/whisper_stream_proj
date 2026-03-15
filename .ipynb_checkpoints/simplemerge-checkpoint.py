class SimpleMergeStrategy:
    def merge(self, existing_text, new_text, match_info):
        merged_list = existing_text.split() + new_text.split()[match_info['overlap_length']:]
        return " ".join(merged_list)