import openai

# OPENAI_KEY = "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"

def compute_embedding(text, model="text-embedding-ada-002"):
    # Clean the text a bit to generate more accurate embeddings with less noise
    text = text.replace("\n", " ")
    return openai.Embedding.create(
        input=[text],
        model=model,
    )

sentence_embedding = compute_embedding(
    text="I will be the best in the world!",
)
print(f"Sentence embedding: {sentence_embedding}")
