import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import os
import gc

def extract_model_response(generated_text):
    start_tag = "[|assistant|]"
    end_tag = "[|endofturn|]"

    start_idx = generated_text.rfind(start_tag)
    end_idx = generated_text.rfind(end_tag)

    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        response = generated_text[start_idx + len(start_tag):end_idx].strip()
        return response
    else:
        response = generated_text[start_idx + len(start_tag):].strip()
        return response

def get_device():
    if torch.backends.mps.is_available():
        return "mps"
    elif torch.cuda.is_available():
        return "cuda"
    else:
        return "cpu"

class Generator:
    def __init__(self):
        os.environ["TOKENIZERS_PARALLELISM"] = "true"
        self.model_id = "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct"
        self.device = get_device()

        print(f"사용 중인 장치: {self.device}")

        if self.device == "cuda":
            os.environ["TOKENIZERS_PARALLELISM"] = "true"
        else:
            os.environ["TOKENIZERS_PARALLELISM"] = "false"

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        ).to(device=self.device)

    def generate_model(self, request):
        input_ids = self.tokenizer.apply_chat_template(
            request.history,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        )

        with torch.no_grad():
            outputs = self.model.generate(
                input_ids.to(self.model.device),
                max_new_tokens=1024,
                do_sample=False,
                eos_token_id=self.tokenizer.eos_token_id
            )

        generated_text = self.tokenizer.decode(outputs[0].detach().cpu())
        del outputs
        response = extract_model_response(generated_text)

        if self.device == "cuda": torch.cuda.empty_cache()
        elif self.device == "mps": torch.mps.empty_cache()

        gc.collect()

        # 답변을 요약해서 대화 히스토리에 저장하기 위한 모델 추론 한번 더
        instruction_summary = "다음은 사용자가 질문한 내용에 관한 답변이며 3줄 이내로 질문과 내용을 최대한 정리 해주세요.\n" + str(response)
        input_ids2 = self.tokenizer.apply_chat_template(
            [{"role": "user", "content": instruction_summary}],
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        )

        with torch.no_grad():
            outputs = self.model.generate(
                input_ids2.to(self.model.device),
                max_new_tokens=128,
                do_sample=False,
                eos_token_id = self.tokenizer.eos_token_id
            )

        generated_text = self.tokenizer.decode(outputs[0].detach().cpu())
        del outputs
        response_summary = extract_model_response(generated_text)

        if self.device == "cuda": torch.cuda.empty_cache()
        elif self.device == "mps": torch.mps.empty_cache()

        gc.collect()

        print(response)
        print(response_summary)

        return response, response_summary

