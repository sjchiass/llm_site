from ollama import generate
from pelican.utils import slugify
from datetime import datetime
import os
import glob
import json
from random import choice, randint

files = glob.glob("./content/*.md")
for f in files:
    os.remove(f)


# A simple class to give the LLM a system prompt and save its context
class PugFriend:
    def __init__(self, system=None):
        self.context = None
        self.system = system

    def gen(self, prompt):
        response = generate(
            model="llama3.2",
            system=self.system,
            prompt=prompt,
            context=self.context,
            options={"num_ctx": 8192},
        )
        self.context = response.context
        return response.response

    def get_context(self):
        return self.context

    def set_context(self, context):
        self.context = context


# A function for creating a blog post
# An initial post is written, then 1-3 other pugs will comment a few times
def create_post(name, category, text):
    with open(f"./content/{name}.md", "w") as f:
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
        for comment_thread in range(choice([1, 2, 3])):
            # For the comments, create a pug copy so that it doesn't remember...
            saved_context = pug.get_context()

            # Don't have the same pug post twice. It's weird.
            pug_friend = choice([x for x in friends if x["name"] not in done_pugs])
            done_pugs.append(pug_friend["name"])

            # Start the conversation
            critic_reply = pug_friend["llm"].gen(
                "You are browing a food blogger's blog. Write a succinct reply to this post: \""
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
                    "A food critic has added the following comment, write back a succinct reply: "
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
                    'The author of the blog has replied to your post, answer them back very succinctly: "'
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
            pug.set_context(saved_context)
            f.write("<hr>")


# Create a pirate pug chef
pug = PugFriend(
    "Your name is PugBeard. You are a pirate pug who has become a food blogger. You come up with recipes while sailing the seas for treasure. You are an enthusiastic programmer of R and Python."
)

other_pugs = json.loads(open("./other_pugs.json", "r").read())
other_pugs_emojis = json.loads(open("./other_pugs_emojis.json", "r").read())
friends = []

# Each friend pug gets their own prompt, context and emoji
for x in other_pugs.keys():
    friends.append(
        {
            "name": x,
            "prompt": other_pugs[x],
            "llm": PugFriend(other_pugs[x]),
            "emoji": other_pugs_emojis[x],
        }
    )

#
# Post generation
#
# Say hello
create_post(
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
        pug.gen(
            "Come up with a name for a mystical ingredient important in magical Christmas treats. Only answer with the name please."
        ),
        "Ingredients",
        pug.gen(
            "Now pretend you are a food blogger and write about your adventure in acquiring the mystical ingredient. Have fun with it!"
        ),
    )

    # Post a recipe
    create_post(
        pug.gen(
            "Come up with a name for Christmas treat dish. Only answer with the name please."
        ),
        "Recipes",
        pug.gen(
            "Now pretend you are a food blogger and write a short post for the recipe of the Christmas treat. After describing it a little, make sure to include the recipe!"
        ),
    )

    # Post a code workshop
    create_post(
        pug.gen(
            "Come up with a title for a blogpost about using Python code to generate Christmas treat names. Only answer with the name please."
        ),
        "Python",
        pug.gen(
            "Now pretend you are a Python coder blogger and write about the Christmas treat generator code. Make it encouraging and welcoming for beginners."
        ),
    )

    # Post a code workshop
    create_post(
        pug.gen(
            "Come up with a title for a blogpost about using R and ggplot2 code to generate a Christmas treat data visualization. Only answer with the name please."
        ),
        "R",
        pug.gen(
            "Now pretend you are a R coder blogger and write a blogpost about using R and ggplot2 code to generate a Christmas treat data visualization. Make it encouraging and welcoming for beginners."
        ),
    )

    # Post an adventure
    create_post(
        pug.gen(
            "Think of a place you had a fantastic pirate pug adventure. Only answer with the name please."
        ),
        "Adventures",
        pug.gen(
            "Now pretend you are a food blogger and tell me all about your fantastic pirate pug adventure. Tell me a good story!"
        ),
    )

    # Post a recipe
    create_post(
        pug.gen(
            "Come up with a name for Christmas treat dish. Only answer with the name please."
        ),
        "Recipes",
        pug.gen(
            "Now pretend you are a food blogger and write a short post for the recipe of the Christmas treat. After describing it a little, make sure to include the recipe!"
        ),
    )

# Say goodbye
create_post(
    "Last Post",
    "Life",
    pug.gen(
        "Pretend you're a food blogger but that this is your last post. You enjoyed cooking, but you are a pirate pug at heart. Tell us how you're going to return to the pirate pug life, but that you will always remember the fun you had writing your food blog. You're off to a new adventure!"
    ),
)
