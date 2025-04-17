import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import os

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
            low_cpu_mem_usage=True
        ).to(device=self.device)

    def generate_model(self, request):
        input_ids = self.tokenizer.apply_chat_template(
            request.history,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        )

        # 추론 모드로 전환해서 좀 더 빠른 답변을 유도
        with torch.inference_mode():
            outputs = self.model.generate(
                input_ids.to(self.model.device),
                max_new_tokens=512,
                do_sample=False
            )

        generated_text = self.tokenizer.decode(outputs[0])
        response = extract_model_response(generated_text)

        # 답변을 요약해서 대화 히스토리에 저장하기 위한 모델 추론 한번 더
        instruction_summary = "다음은 사용자가 질문한 내용에 관한 답변이며 내용을 최대한 정리 해주세요.\n" + str(response)
        input_ids2 = self.tokenizer.apply_chat_template(
            [{"role": "user", "content": instruction_summary}],
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        )

        with torch.inference_mode():
            outputs = self.model.generate(
                input_ids2.to(self.model.device),
                max_new_tokens=128,
                do_sample=False
            )

        generated_text = self.tokenizer.decode(outputs[0])
        response_summary = extract_model_response(generated_text)

        return response, response_summary

