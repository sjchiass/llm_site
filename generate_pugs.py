from ollama import generate
import os
import json
from tqdm import tqdm

raw_data = json.loads(open("./other_pugs_raw.json", "r").read())

prompts = [
    generate(
        model="llama3.2",
        prompt=f"""Imagine me as a cute pug named "{name}". Give me the following appearance: "{description}". Make this my favorite emoji: {emoji}. Based on this information, describe \n\n1. my appearance,\n2. my backstory,\n3. my personality,\n4. my coding style,\n5. my favorite treats,\n6. my favourite programming language,\n7. my manner of speaking\n\nAnswer as if addressing me (refer to me as 'you').""",
    ).response
    for name, description, emoji in tqdm(raw_data, desc="generating prompts")
]

data = []
for (name, description, emoji), prompt in zip(raw_data, prompts):
    print(name, description, prompt, emoji)
    data.append(
        {"name": name, "description": description, "prompt": prompt, "emoji": emoji}
    )

with open("other_pugs.json", "w") as f:
    f.write(json.dumps(data, indent=4))
