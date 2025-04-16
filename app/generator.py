import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import os

def extract_model_response(generated_text):
    # [|assistant|]가 있는 부분부터 잘라내기
    start_idx = generated_text.rfind("[|assistant|]")
    if start_idx != -1:
        # -13인 이유 마지막에 붙는 [|endofturn|] 제거를 위함
        response = generated_text[start_idx + len("[|assistant|]"):-13].strip()
        return response
    else:
        return

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

        return response

