from ollama import generate
from pelican.utils import slugify
from datetime import datetime
import os
import glob

files = glob.glob("./content/*.md")
for f in files:
    os.remove(f)

# A simple class to give the LLM a system prompt and save its context
class ChefPug:
    def __init__(self, system=None):
        self.context = None
        self.system = system

    def gen(self, prompt):
        response = generate(
            model="llama3.2", system=self.system, prompt=prompt, context=self.context
        )
        self.context = response.context
        return response.response

# Create a pirate pug chef
pug = ChefPug(
    "Your name is PugBeard. You are a pirate pug who has become a food blogger. You come up with recipes while sailing the seas for treasure. You are an enthusiastic programmer of R and Python."
)

# Say hello
with open("./content/introduction.md", "w") as f:
    f.writelines(
        [
            f"Title: First post\n",
            f"Date: {datetime.now().isoformat()}\n",
            "Category: Life\n",
            "\n\n",
            pug.gen(
                "Pretend you're a food blogger and write your first post saying hello to everyone. Tell us about your plans for your new food blog."
            ),
        ]
    )

# Generate posts, only 5 to make it all fit on one page
for i in range(5):
    # Post about acquiring special ingredients
    if i % 5 == 1:
        filename = (
            "./content/"
            + slugify(
                pug.gen(
                    "Come up with a name for a mystical ingredient important in magical Christmas treats. Only answer with the name please."
                )
            )
            + ".md"
        )

        with open(filename, "w") as f:
            f.writelines(
                [
                    f"Title: {pug.gen('Repeat the name of the mystical ingredient in title case.')}\n",
                    f"Date: {datetime.now().isoformat()}\n",
                    "Category: Special Ingredients\n",
                    "\n\n",
                    pug.gen(
                        "Now pretend you are a food blogger and write about your adventure in acquiring the mystical ingredient. Have fun with it!"
                    ),
                ]
            )
    # Post about past travels
    elif i % 5 == 3:
        filename = (
            "./content/"
            + slugify(
                pug.gen(
                    "Think of a place you had a fantastic pirate pug adventure. Only answer with the name please."
                )
            )
            + ".md"
        )

        with open(filename, "w") as f:
            f.writelines(
                [
                    f"Title: {pug.gen('Repeat the name of the fantastic pirate pug adventure place in title case.')}\n",
                    f"Date: {datetime.now().isoformat()}\n",
                    "Category: Adventure\n",
                    "\n\n",
                    pug.gen(
                        "Now pretend you are a food blogger and tell me all about your fantastic pirate pug adventure. Tell me a good story!"
                    ),
                ]
            )
    # Post a recipe
    else:
        filename = (
            "./content/"
            + slugify(
                pug.gen(
                    "Come up with a name for Christmas treat dish. Only answer with the name please."
                )
            )
            + ".md"
        )

        with open(filename, "w") as f:
            f.writelines(
                [
                    f"Title: {pug.gen('Repeat the name of the treat in title case.')}\n",
                    f"Date: {datetime.now().isoformat()}\n",
                    "Category: Recipes\n",
                    "\n\n",
                    pug.gen(
                        "Now pretend you are a food blogger and write a short post for the recipe of the Christmas treat. After describing it a little, make sure to include the recipe!"
                    ),
                ]
            )

# Say goodbye
with open("./content/gooodbye.md", "w") as f:
    f.writelines(
        [
            f"Title: Last post\n",
            f"Date: {datetime.now().isoformat()}\n",
            "Category: Life\n",
            "\n\n",
            pug.gen(
                "Pretend you're a food blogger but that this is your last post. You enjoyed cooking, but you are a pirate pug at heart. Tell us how you're going to return to the pirate pug life, but that you will always remember the fun you had writing your food blog. You're off to a new adventure!"
            ),
        ]
    )