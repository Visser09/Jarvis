from llama_cpp import Llama

model_path = "D:\models\Phi-3-mini-4k-instruct-q4.gguf"

llm = Llama(model_path=model_path, n_ctx=4096)

response = llm("Q: What's 3 + 4?\nA:", max_tokens=32, stop=["Q:", "\n"])
print(response["choices"][0]["text"].strip())
