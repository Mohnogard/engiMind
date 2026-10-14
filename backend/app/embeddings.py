from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def count_tokens(text):
    return len(model.tokenizer(text)["input_ids"])

if __name__ == "__main__":
    print(len(model.encode("hello\n")))   # should print 384