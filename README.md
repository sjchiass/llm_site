## What this is

It's my first attempt at using LLMs programatically. I use the Llama LLM to generate a few starter prompts (character backgrounds, blog name, post titles) then generate more content from that. LLMs are further used to generate conversations about the blog posts, and LLMs are used to decide when the conversations are done. Finally, an LLM generates prompts for an image synthesize to create little images to go along each post.

All of this is not too hard to do if you have an A[PI like Ollama](https://github.com/ollama/ollama-python) to take control of LLMs. You can manipulate their system prompts and control their contexts. You can make them forget things and re-run repeatedly until they output what you want (ex: a yes/no answer to a question).

## Site

Viewed at: https://sjchiass.github.io/llm_site/

## Setup

Create a python environment for python 3.11:

`conda create -n ollama_site python=3.11`

After activating the environment, install some packages:

`pip install pelican[markdown] ollama python-slugify`

Before generating posts, make sure to install [ollama](https://ollama.com/) and make sure `ollama serve` is running.

In order to also generate images, have a look at my setup guides [here](https://github.com/sjchiass/ml-pug-stickers).

## Program flow

Optional: you can regenerate the pug friends by running `generate_pugs.py`. The pug friends are generated from initial prompts in the `other_pugs_raw.json`.

**Generate pages** Run the `generate_posts.py` script to generate all of the posts, comments and image prompts.

What this does:

  - Creates a new PugBeard character with a blog (name, bio) with a recipe style to follow.
  - All alternate-reality PugBeards go into a list with their URLs so they can link to each other.
  - For each blog, various posts are created: an intro post, an adventure for a secret ingredient, a recipe for the secret ingredient, etc.
  - For each post, the blog post text is generated, then optionally an image to accompany the text, and then optionally a discussion thread with 5 other Pug Friends. (The Pug Friends will usually congragulate PugBeard on a job well done.)

Optional: run the `generate_images.py` from a Python environment able to run Stable Diffusion XL. It will generate images for each post based on the prompts generated in `sd_generation_instructions.json`.
