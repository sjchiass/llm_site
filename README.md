## Site

Viewed at: https://sjchiass.github.io/llm_site/

## Setup

Create a python environment for python 3.11:

`conda create -n ollama_site python=3.11`

After activating the environment, install some packages:

`pip install pelican[markdown] ollama`

Before generating posts, make sure to install [ollama](https://ollama.com/) and make sure `ollama serve` is running.

## Notes

I've brought over some other personalities from https://github.com/sjchiass/rag-pugs They could use a bit of work so that they write more like blog commenters. The generation of their prompts could also be included in this repo.
