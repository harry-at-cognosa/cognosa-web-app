import re

class StringValidator:
    # Allowed characters
    # This includes accented characters from common languages
    # Replace any character that's not in allowed set with a space
    regex_1 = re.compile(r"[^-_a-zA-Z0-9À-ÖØ-öø-ÿĀ-žŒœŠšŸÿŽž'`\"\.\(\)\[\]]")
    regex_2 = re.compile(r'\s+')    
    @classmethod
    def replace_non_common_lang(cls, v: str, min_length: int = 0, max_length: int = 65535) -> str:
        if not isinstance(v, str):
            raise ValueError('Input must be string')
        # Replace any character that's not in allowed set with a space
        cleaned = cls.regex_1.sub(' ', v)
        # Replace multiple consecutive spaces with single space and strip
        cleaned = cls.regex_2.sub(' ', cleaned).strip()
        # check minimum and maximum length after cleaning
        if min_length and (len(cleaned) < min_length):
            raise ValueError('Input must contain at least 3 valid characters')
        if max_length and (len(cleaned) > max_length):
            raise ValueError(f'Input too long (>{max_length} characters).')
        return cleaned
