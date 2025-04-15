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
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        self.model_id = "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct"
        self.device = get_device()

        print(f"사용 중인 장치: {self.device}")

        if self.device == "cuda":
            # nvidia에서만 가능
            self.quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True
            )

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16,
                trust_remote_code=True,
                low_cpu_mem_usage=True,
                quantization_config=self.quantization_config
            ).to(device=self.device)

        else:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=torch.float32,
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

        outputs = self.model.generate(
            input_ids.to(self.model.device),
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )

        generated_text = self.tokenizer.decode(outputs[0])
        print(generated_text)
        response = extract_model_response(generated_text)

        print(response)
        return response

