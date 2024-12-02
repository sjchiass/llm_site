from ollama import generate
from pelican.utils import slugify
from datetime import datetime
import os
import glob

files = glob.glob("./content/*")
for f in files:
    os.remove(f)


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


pug = ChefPug(
    "You are a pirate pug who has become a food blogger. You come up with recipes while sailing the seas for treasure. You are an enthusiastic programmer of R and Python."
)

for i in range(5):
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
