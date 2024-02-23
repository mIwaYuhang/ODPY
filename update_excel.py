
import subprocess
import os
import shutil
import stat

for i, j, k in [
    [
        "https://github.com/Kengxxiao/ArknightsGameData.git", "zh_CN", "data"
    ],
    [
        "https://github.com/Kengxxiao/ArknightsGameData_YoStar.git", "en_US", "data-global"
    ]
]:

    subprocess.run(
        [
            "git", "clone",
            "-n",  "--depth=1", "--filter=tree:0",
            i, "tmp"
        ]
    )

    subprocess.run(
        [
            "git", "sparse-checkout", "set",
            f"{j}/gamedata/excel/"
        ], cwd="tmp"
    )

    subprocess.run(
        [
            "git", "checkout"
        ], cwd="tmp"
    )

    if os.path.isdir(f"tmp/{j}/gamedata/excel/"):
        shutil.rmtree(f"{k}/excel")
        shutil.move(f"tmp/{j}/gamedata/excel/", k)

    def rmtree_onerror(function, path, excinfo):
        os.chmod(path, stat.S_IWUSR)
        function(path)

    shutil.rmtree("tmp/", onerror=rmtree_onerror)
