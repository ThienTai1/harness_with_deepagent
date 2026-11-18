from langchain_ollama import ChatOllama


model = ChatOllama(
    model="gemma4:e4b-mlx",
    temperature=1.1,
    # base_url="http://localhost:11434" # Bật dòng này nếu Ollama chạy ở cổng khác
)
