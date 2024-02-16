
import subprocess
import os
import shutil
import stat

subprocess.run(
    [
        "git", "clone",
        "-n",  "--depth=1", "--filter=tree:0",
        "https://github.com/Kengxxiao/ArknightsGameData.git", "tmp"
    ]
)

subprocess.run(
    [
        "git", "sparse-checkout", "set",
        "zh_CN/gamedata/excel/"
    ], cwd="tmp"
)

subprocess.run(
    [
        "git", "checkout"
    ], cwd="tmp"
)

if os.path.isdir("tmp/zh_CN/gamedata/excel/"):
    shutil.rmtree("data/excel/")
    shutil.move("tmp/zh_CN/gamedata/excel/", "data/")


def rmtree_onerror(function, path, excinfo):
    os.chmod(path, stat.S_IWUSR)
    function(path)


shutil.rmtree("tmp/", onerror=rmtree_onerror)
