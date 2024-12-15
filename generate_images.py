from diffusers import AutoPipelineForText2Image
import torch
import json


pipeline = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    variant="fp16",
).to("cuda:0")

# To save a bit of memory
# pipeline.enable_model_cpu_offload()

data = json.load(open("./sd_generation_instructions.json", "r"))

# Generate image from instructions, keep file size low
# Use 1024x576 dimensions which allow video diffusion later (for GIFs?)
for n, d in enumerate(data):
    print(f"Gednerating image {n+1} of {len(data)} ...")
    prompt = d["prompt"]
    output_path = d["output_path"]
    pipeline(prompt, width=1024, height=576).images[0].save(
        output_path, optimize=True, quality=50
    )
