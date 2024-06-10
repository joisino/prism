from chatgpt_util import send_message


class ChatGPTTranslator:
    def translate_text(self, input_text, target_lang="German"):
        res = send_message("Directly translate English to {}: {}".format(target_lang, input_text))
        return res
