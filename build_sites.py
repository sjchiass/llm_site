import glob
import subprocess
import shutil
import os

if os.path.isdir("./output"):
    shutil.rmtree("./output")

if os.path.isdir("./main_site/output"):
    shutil.rmtree("./main_site/output")
subprocess.run(["pelican"], cwd="./main_site/")
shutil.copytree("./main_site/output", "./output", dirs_exist_ok=True)

for sub_site in glob.glob("./sub_sites/*/"):
    print(sub_site)
    if os.path.isdir(sub_site+"output"):
        shutil.rmtree(sub_site+"output")
    subprocess.run(["pelican"], cwd=sub_site)
    shutil.copytree(sub_site+"output", sub_site.replace("sub_sites", "output"), dirs_exist_ok=True)
