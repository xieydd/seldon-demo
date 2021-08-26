import base64
import json
from subprocess import PIPE, Popen, run

import numpy as np
from transformers import GPT2Tokenizer, TFGPT2LMHeadModel

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
input_text = "I enjoy working in Seldon"
input_ids = tokenizer.encode(input_text, return_tensors="tf")
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
cmd = {
    "method": "POST",
    "header": {"Content-Type": ["application/json"]},
    "url": url,
    "body": base64.b64encode(bytes(json.dumps(payload), "utf-8")).decode("utf-8"),
}

with open("vegeta_target.json", mode="w") as file:
    json.dump(cmd, file)
    file.write("\n\n")