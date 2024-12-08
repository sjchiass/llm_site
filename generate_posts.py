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

# Cleanup
if os.path.isdir("./main_site"):
    shutil.rmtree("./main_site")
if os.path.isdir("./sub_sites"):
    shutil.rmtree("./sub_sites")

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
            model="llama3.2",
            system=self.system,
            prompt=prompt,
            context=self.context,
            options={"num_ctx": 32768},
        )
        self.context = response.context
        return response.response

    def gen_oneline(self, prompt):
        while True:
            response = generate(
                model="llama3.2",
                system=self.system,
                prompt=prompt,
                context=self.context,
                options={"num_ctx": 32768},
            )
            if "\n" not in response.response:
                print("Got one line, done ...")
                return response.response
            else:
                print("Got more than one line, rerun ...")

    def get_context(self):
        return self.context

    def set_context(self, context):
        self.context = context


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
            model="llama3.2",
            prompt="Give me the name of your food blog that hints at the kind of recipes it has. Only response with the name.",
            system=self.pugbeard_prompt,
        ).response.replace('"', "")
        self.bio = generate(
            model="llama3.2",
            prompt="Give me a one sentence bio of yourself.",
            system=self.pugbeard_prompt,
        ).response.replace('"', "")
        self.pugbeard_prompt += f'\nYour food blog is named {self.name} and this is the bio you wrote for yourself: "{self.bio}"'


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
        f.write("\n\n# Comments\n\n")
        done_pugs = []
        for comment_thread in range(choice([1, 2, 3, 4, 5])):
            # For the comments, create a pug copy so that it doesn't remember...
            saved_context = pug.get_context()

            # Don't have the same pug post twice. It's weird.
            pug_friend = choice([x for x in friends if x["name"] not in done_pugs])
            done_pugs.append(pug_friend["name"])

            # Start the conversation
            critic_reply = pug_friend["llm"].gen(
                f'You are browsing the {blog.name} foodie blog written by {pug.name}. Write a succinct comment to this post from the blog: "'
                + text
                + '"'
            )
            f.write(
                f"\n\n<hr>### {pug_friend['emoji']}{pug_friend['name']}{pug_friend['emoji']}\n\n{critic_reply}\n"
            )

            odds = 1

            while True:
                # Reply from author
                author_reply = pug.gen(
                    f"A reader named {pug_friend['name']} has added the following comment, write back a succinct reply: "
                    + '"'
                    + critic_reply
                    + '"'
                )
                f.write(f"\n\n<hr>### PugBeard\n\n{author_reply}\n")
                if randint(0, odds) != 0:
                    break
                else:
                    odds *= 2
                # Reply back from friend
                critic_reply = pug_friend["llm"].gen(
                    f"{pug.name} has replied to your post in the {blog.name} foodie blog comment section, answer them back very succinctly: "
                    + author_reply
                    + '"'
                )
                f.write(
                    f"\n\n<hr>### {pug_friend['emoji']}{pug_friend['name']}{pug_friend['emoji']}\n\n{critic_reply}\n"
                )
                if randint(0, odds) != 0:
                    break
                else:
                    odds *= 2
                # break now because conversations seem to loop at this point
                break
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

# SITEURL = "https://sjchiass.github.io/llm_site"
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
    print(f"Site will be at {siteurl}/{blog.url}")
    
    if site_num == 0:
        Path(f"./main_site/content/images").mkdir(parents=True, exist_ok=True)
        root_path = "main_site"
    else:
        Path(f"./sub_sites/{slugify(blog.url)}/content/images").mkdir(parents=True, exist_ok=True)
        root_path = f"sub_sites/{slugify(blog.url)}"
    
    shutil.copy("./pug_only.png", root_path+"/content/images/pug_only.png")

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
