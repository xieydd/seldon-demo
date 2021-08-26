import json

import numpy as np
import requests
from transformers import GPT2Tokenizer

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
input_text = "I enjoy working in Seldon"
count = 0
max_gen_len = 10
gen_sentence = input_text
while count < max_gen_len:
    input_ids = tokenizer.encode(gen_sentence, return_tensors="tf")
    shape = input_ids.shape.as_list()
    payload = {
        "inputs": [
            {
                "name": "input_ids:0",
                "datatype": "INT32",
                "shape": shape,
                "data": input_ids.numpy().tolist(),
            },
            {
                "name": "attention_mask:0",
                "datatype": "INT32",
                "shape": shape,
                "data": np.ones(shape, dtype=np.int32).tolist(),
            },
        ]
    }

    url = 'http://%s/seldon/default/gpt2/v2/models/gpt2/infer'%os.getenv("SELDON_URL")
    
    ret = requests.post(
        url, json=payload
    )

    try:
        res = ret.json()
    except:
        continue

    # extract logits
    logits = np.array(res["outputs"][1]["data"])
    logits = logits.reshape(res["outputs"][1]["shape"])

    # take the best next token probability of the last token of input ( greedy approach)
    next_token = logits.argmax(axis=2)[0]
    next_token_str = tokenizer.decode(
        next_token[-1:], skip_special_tokens=True, clean_up_tokenization_spaces=True
    ).strip()
    gen_sentence += " " + next_token_str
    count += 1

print(f"Input: {input_text}\nOutput: {gen_sentence}")