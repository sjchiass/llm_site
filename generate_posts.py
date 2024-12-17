from ollama import generate
from slugify import slugify
from datetime import datetime
import os
import glob
import json
from random import choice, randint
import re
import argparse
from pathlib import Path
import shutil

MODEL = "llama3.1"
CONTEXT_WINDOW = 32768
MAKE_IMAGES = True
MAKE_CONVERSATIONS = True

SD_GENERATION_INSTRUCTION = []

# Cleanup
if os.path.isdir("./main_site"):
    shutil.rmtree("./main_site")
if os.path.isdir("./sub_sites"):
    shutil.rmtree("./sub_sites")

# Delete image generation instructions if they exist,
# so that images are not generated with old instructions
if os.path.exists("./sd_generation_instructions.json"):
    os.remove("./sd_generation_instructions.json")
if os.path.exists("./sd_generation_instructions_updated.json"):
    os.remove("./sd_generation_instructions_updated.json")

parser = argparse.ArgumentParser(
    prog="ProgramName",
    description="What the program does",
    epilog="Text at the bottom of help",
)

parser.add_argument("variations", nargs="*")

args = parser.parse_args()


# A simple class to give the LLM a system prompt and save its context
class PugFriend:
    def __init__(self, name, system=None):
        self.context = None
        self.name = name
        self.system = system

    def gen(self, prompt):
        response = generate(
            model=MODEL,
            system=self.system,
            prompt=prompt,
            context=self.context,
            options={"num_ctx": CONTEXT_WINDOW},
        )
        self.context = response.context
        return response.response

    def gen_oneline(self, prompt):
        while True:
            response = generate(
                model=MODEL,
                system=self.system,
                prompt=prompt,
                context=self.context,
                options={"num_ctx": CONTEXT_WINDOW},
            )
            if "\n" not in response.response:
                self.context = response.context
                return response.response

    def get_context(self):
        return self.context

    def set_context(self, context):
        self.context = context


# A simple class to answer Y/N questions
class Answer:
    def __init__(self):
        self.system = "Only answer with Yes or No. If something is true, answer Yes. If something is false, answer No."

    def answer(self, prompt):
        while True:
            response = generate(
                model=MODEL,
                system=self.system,
                prompt=prompt,
                options={"num_ctx": CONTEXT_WINDOW, "num_predict": 1},
            ).response.lower()
            if response in ["yes", "no"]:
                return response


# A class for storing site information
class Blog:
    def __init__(
        self,
        variation,
        base_prompt="Your name is PugBeard. You are an old pirate pug who has become a food blogger. You come up with recipes while sailing the seas for treasure. You are an enthusiastic programmer of R and Python. Your food blog only has ",
    ):
        self.pugbeard_prompt = base_prompt + variation
        self.url = slugify(variation)
        self.name = generate(
            model=MODEL,
            prompt="Give me the name of your food blog that hints at the kind of recipes it has. Only response with the name.",
            system=self.pugbeard_prompt,
        ).response.replace('"', "")
        self.bio = generate(
            model=MODEL,
            prompt="Give me a one sentence bio of yourself.",
            system=self.pugbeard_prompt,
        ).response.replace('"', "")
        self.pugbeard_prompt += f'\nYour food blog is named {self.name} and this is the bio you wrote for yourself: "{self.bio}"'


class PromptMaker:
    def __init__(
        self,
        system="You only answer with short prompts that can be used with the Stable Diffusion text-to-image generator. You do not use proper nouns. You enclose your prompt in curly brackets {}.",
    ):
        self.system = system

    def gen(self, prompt):
        while True:
            response = generate(
                model=MODEL,
                system=self.system,
                prompt=prompt,
                options={"num_ctx": CONTEXT_WINDOW},
            ).response
            response = re.search(r"\{(.*?)\}", response)
            if response is not None and len(response.group(1)) > 10:
                return response.group(1)


# A function for creating a blog post
# An initial post is written, then 1-3 other pugs will comment a few times
def create_post(blog, root_path, name, category, text):
    with open(f"./{root_path}/content/{name}.md", "w") as f:
        f.writelines(
            [
                f"Title: {name.title()}\n",
                f"Date: {datetime.now().isoformat()}\n",
                f"Category: {category}\n",
                "\n\n",
                text,
            ]
        )
        if MAKE_IMAGES:
            sd_prompt = prompt_maker.gen(text)
            fname = slugify(datetime.now().isoformat())
            f.write(f"\n\n![{sd_prompt}]({{static}}/images/{fname}.jpg)\n\n")
            SD_GENERATION_INSTRUCTION.append(
                {
                    "output_path": f"./{root_path}/content/images/{fname}.jpg",
                    "prompt": sd_prompt,
                }
            )
        if MAKE_CONVERSATIONS:
            f.write("\n\n# Comments\n\n")
            done_pugs = []
            for comment_thread in range(5):
                # For the comments, create a pug copy so that it doesn't remember...
                saved_context = pug.get_context()

                # Don't have the same pug post twice. It's weird.
                pug_friend = choice([x for x in friends if x["name"] not in done_pugs])
                done_pugs.append(pug_friend["name"])

                conversation = ""

                # Start the conversation
                critic_reply = pug_friend["llm"].gen(
                    f'You are browsing the {blog.name} foodie blog written by {pug.name}. Write a succinct comment to this post from the blog: "'
                    + text
                    + '"'
                )
                conversation += f"\n\n<hr>### {pug_friend['emoji']}{pug_friend['name']}{pug_friend['emoji']}\n\n{critic_reply}\n"

                while True:
                    # Reply from author
                    author_reply = pug.gen(
                        f"A reader named {pug_friend['name']} has added the following comment, write back a succinct reply: "
                        + '"'
                        + critic_reply
                        + '"'
                    )
                    conversation += f"\n\n<hr>### PugBeard\n\n{author_reply}\n"

                    if (
                        get_answer.answer(
                            "Is the following conversation starting to repeat itself?\n\n"
                            + conversation
                        )
                        == "yes"
                    ):
                        break

                    # Reply back from friend
                    critic_reply = pug_friend["llm"].gen(
                        f"{pug.name} has replied to your post in the {blog.name} foodie blog comment section, answer them back very succinctly: "
                        + author_reply
                        + '"'
                    )
                    conversation += f"\n\n<hr>### {pug_friend['emoji']}{pug_friend['name']}{pug_friend['emoji']}\n\n{critic_reply}\n"

                    if (
                        get_answer.answer(
                            "Is the following conversation starting to repeat itself?\n\n"
                            + conversation
                        )
                        == "yes"
                    ):
                        break

                f.write(conversation)
                pug.set_context(saved_context)
                f.write("<hr>")


variations = [
    "recipes inspired by programming",
    "low-carb ketogenic recipes",
    "gluten-free recipes",
    "vegan recipes",
    "nut-free recipes",
    "dog-safe recipes for dogs",
    "meat-only recipes",
    "recipes made with abtract ingredients, like time, emotion, and identity",
    "recipes inspired by Lord of the Rings",
]

base_prompt = "Your name is PugBeard. You are an old pirate pug who has become a food blogger. You come up with recipes while sailing the seas for treasure. You are an enthusiastic programmer of R and Python. Your food blog only has "

websites = []

for variation in variations:
    websites.append(Blog(variation))

# The SITEURL is read from your pelicanconf.py file, so you can change it there
with open("./pelicanconf.py", "r+") as f:
    conf = f.read()
    siteurl = re.search(r"SITEURL = \"([^\"]+)\"", conf)[1]
    siteurl_list = []
    for site_num, blog in enumerate(websites):
        if site_num == 0:
            siteurl_list.append((blog.name, siteurl))
        else:
            siteurl_list.append((blog.name, siteurl + "/" + blog.url))

themes = ["08", "09", "0a", "0b", "0c", "0d", "0e", "0f"]

for site_num, blog in enumerate(websites):
    print(f"Generating '{blog.name}', {site_num+1} out of {len(websites)} ...")

    if site_num == 0:
        Path(f"./main_site/content/images").mkdir(parents=True, exist_ok=True)
        root_path = "main_site"
        print(f"Site will be at {siteurl}")
    else:
        Path(f"./sub_sites/{slugify(blog.url)}/content/images").mkdir(
            parents=True, exist_ok=True
        )
        root_path = f"sub_sites/{slugify(blog.url)}"
        print(f"Site will be at {siteurl}/{blog.url}")

    shutil.copy("./pug_only.png", root_path + "/content/images/pug_only.png")

    # Prepare a list of urls and names for the other sites
    other_urls = (
        "["
        + ",\n    ".join(
            [
                f"(\"{name}\", '{url}')"
                for name, url in siteurl_list
                if name != blog.name
            ]
        )
        + "]"
    )

    # The configuration file is a Python script, so to overwrite values, just
    # declare them again
    with open("./pelicanconf.py", "r+") as f:
        conf = f.read()
        conf += f'\nSITENAME = "{blog.name}"'
        if site_num == 0:
            conf += f'\nSITEURL = "{siteurl}"'
        else:
            conf += f'\nSITEURL = "{siteurl}/{blog.url}"'
        conf += f'\nBIO = "{blog.bio}"'
        conf += f"\nMENUITEMS = {other_urls}"
        conf += f"\nCOLOR_THEME = '{themes[site_num % 8]}'"

    with open(f"./{root_path}/pelicanconf.py", "w") as f:
        f.write(conf)

    # Create a pirate pug chef
    pug = PugFriend(
        system=blog.pugbeard_prompt,
        name="PugBeard",
    )

    # Create his friends
    friends = json.loads(open("./other_pugs.json", "r").read())

    for friend in friends:
        friend["llm"] = PugFriend(system=friend["prompt"], name=friend["name"])

    # Create a simple LLM to answer yes/no questions
    get_answer = Answer()

    # Create another simple LLM to generate image generation prompts
    prompt_maker = PromptMaker()

    #
    # Post generation
    #
    # Say hello
    create_post(
        blog,
        root_path,
        "First Post",
        "Life",
        pug.gen(
            "Pretend you're a food blogger and write your first post saying hello to everyone. Tell us about your plans for your new food blog."
        ),
    )

    # A lot of posts can be generated. I think it's better not to do too many.
    for cycle in range(1):
        # Post an ingredient adventure
        create_post(
            blog,
            root_path,
            pug.gen_oneline(
                "Come up with a name for a mystical ingredient important in magical Christmas treats. Only answer with the name please."
            ),
            "Ingredients",
            pug.gen(
                "Now pretend you are a food blogger and write about your adventure in acquiring the mystical ingredient. Have fun with it!"
            ),
        )

        # Post a recipe
        create_post(
            blog,
            root_path,
            pug.gen_oneline(
                "Come up with a name for Christmas treat dish. Only answer with the name please."
            ),
            "Recipes",
            pug.gen(
                "Now pretend you are a food blogger and write a short post for the recipe of the Christmas treat. After describing it a little, make sure to include the recipe!"
            ),
        )

        # Post a code workshop
        create_post(
            blog,
            root_path,
            pug.gen_oneline(
                "Come up with a title for a blogpost about using Python code to generate Christmas treat names. Only answer with the name please."
            ),
            "Python",
            pug.gen(
                "Now pretend you are a Python coder blogger and write about the Christmas treat generator code. Make it encouraging and welcoming for beginners."
            ),
        )

        # Post a code workshop
        create_post(
            blog,
            root_path,
            pug.gen_oneline(
                "Come up with a title for a blogpost about using the R tidyverse and ggplot2 code to generate a Christmas treat data visualization. Only answer with the name please."
            ),
            "R",
            pug.gen(
                "Now pretend you are a R coder blogger and write a blogpost about using the R tidyverse and ggplot2 code to generate a Christmas treat data visualization. Make it encouraging and welcoming for beginners."
            ),
        )

        # Post an adventure
        create_post(
            blog,
            root_path,
            pug.gen_oneline(
                "Think of a place you had a fantastic pirate pug adventure. Only answer with the name please."
            ),
            "Adventures",
            pug.gen(
                "Now pretend you are a food blogger and tell me all about your fantastic pirate pug adventure. Tell me a good story!"
            ),
        )

        # Post a recipe
        create_post(
            blog,
            root_path,
            pug.gen_oneline(
                "Come up with a name for Christmas treat dish. Only answer with the name please."
            ),
            "Recipes",
            pug.gen(
                "Now pretend you are a food blogger and write a short post for the recipe of the Christmas treat. After describing it a little, make sure to include the recipe!"
            ),
        )

    # Say goodbye
    create_post(
        blog,
        root_path,
        "Last Post",
        "Life",
        pug.gen(
            "Pretend you're a food blogger but that this is your last post. You enjoyed cooking, but you are a pirate pug at heart. Tell us how you're going to return to the pirate pug life, but that you will always remember the fun you had writing your food blog. You're off to a new adventure!"
        ),
    )

with open("sd_generation_instructions.json", "w") as f:
    f.write(json.dumps(SD_GENERATION_INSTRUCTION, indent=4))
