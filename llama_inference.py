import modal

stub = modal.Stub("llama-3-1-405b-example")

llama_image = (
    modal.Image.debian_slim()
    .pip_install("transformers", "torch", "accelerate")
    .run_commands("pip install git+https://github.com/huggingface/transformers")
)

@stub.function(
    image=llama_image,
    gpu="a100",
    timeout=600,
)
def run_llama(prompt: str):
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch

    model_id = "meta-llama/Llama-2-405b-chat-hf"
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, 
        torch_dtype=torch.float16, 
        device_map="auto",
    )

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
        )
    
    response = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    return response

@stub.local_entrypoint()
def main():
    prompt = "Explain the concept of quantum entanglement in simple terms."
    response = run_llama.remote(prompt)
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")

if __name__ == "__main__":
    with stub.run():
        main()