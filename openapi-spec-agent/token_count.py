import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import tiktoken
from tqdm import tqdm

# Choose tokenizer
encoding = tiktoken.encoding_for_model("gpt-4o-mini")

# File settings
file_path = "temp.txt"
chunk_size = 2 * 1024 * 1024  # 2 MB chunks
max_workers = os.cpu_count() or 4  # use all available cores

# Get total file size for progress tracking
file_size = os.path.getsize(file_path)

def count_tokens_in_chunk(chunk: str) -> int:
    """Tokenize a chunk and return token count."""
    return len(encoding.encode(chunk))

def read_file_in_chunks(path, size):
    """Generator that yields text chunks from file."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        while True:
            chunk = f.read(size)
            if not chunk:
                break
            yield chunk

token_count = 0
futures = []

with ThreadPoolExecutor(max_workers=max_workers) as executor, tqdm(
    total=file_size, unit="B", unit_scale=True, desc="Processing file"
) as pbar:

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            # Submit to thread pool
            future = executor.submit(count_tokens_in_chunk, chunk)
            futures.append((future, len(chunk)))  # track chunk size for progress bar

            # Optional: limit queued futures to avoid memory bloat
            if len(futures) >= max_workers * 2:
                done, pending = [], []
                for fut, size in futures:
                    if fut.done():
                        token_count += fut.result()
                        pbar.update(size)
                        done.append((fut, size))
                    else:
                        pending.append((fut, size))
                futures = pending

    # Finish remaining futures
    for fut, size in futures:
        token_count += fut.result()
        pbar.update(size)

print(f"\n✅ Total tokens: {token_count:,}")
