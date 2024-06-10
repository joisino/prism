from transformers import T5ForConditionalGeneration, T5Tokenizer


class T5Translator:
    def __init__(self, model_name="t5-base", device="cpu"):
        self.tokenizer = T5Tokenizer.from_pretrained(model_name, model_max_length=2048)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        device = int(device) if device.isdigit() else device
        if device != "cpu":
            self.model = self.model.cuda(device)
        self.device = device

    def translate_text(self, input_text, target_lang="German"):
        batch = self.tokenizer("translate English to {}: {}".format(target_lang, input_text), return_tensors="pt")
        if self.device != "cpu":
            batch = {k: v.cuda(self.device) for k, v in batch.items()}
        res = self.model.generate(**batch, max_length=2048, repetition_penalty=1.5)
        return self.tokenizer.decode(res[0], skip_special_tokens=True)
