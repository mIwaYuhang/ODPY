import UnityPy
import subprocess
from zipfile import ZipFile
import os
import json
import shutil
import requests
import bson

with open("settings.json") as f:
    settings = json.load(f)

legacy_source_versions = settings["legacy_source_versions"]
legacy_activities = settings["legacy_activities"]
source_versions = settings["source_versions"]
target_version = settings["target_version"]


def download_asset_bundle(res_version, asset_bundle_name):
    os.makedirs(res_version, exist_ok=True)
    subprocess.run(
        [
            "curl", "-L", "-O",
            "--output-dir", res_version,
            f"https://ak.hycdn.cn/assetbundle/official/Android/assets/{res_version}/{asset_bundle_name}"
        ]
    )
    with ZipFile(f"{res_version}/{asset_bundle_name}") as f:
        f.extractall(res_version)


for source_version in legacy_source_versions:
    download_asset_bundle(source_version, "torappu.dat")
    download_asset_bundle(source_version, "torappu_index.dat")

for source_version in legacy_activities:
    legacy_activity = legacy_activities[source_version]
    download_asset_bundle(
        source_version,
        os.path.splitext(
            legacy_activity.replace(
                '/', '_'
            ).replace(
                '#', "__"
            )
        )[0]+".dat"
    )

for source_version in source_versions:
    download_asset_bundle(source_version, "torappu.dat")
    download_asset_bundle(source_version, "torappu_index.dat")
    download_asset_bundle(source_version, "gamedata_levels_activities.dat")

download_asset_bundle(target_version, "torappu.dat")
download_asset_bundle(target_version, "torappu_index.dat")
download_asset_bundle(target_version, "gamedata_levels_activities.dat")

res_version_to_torappu_env = {}
res_version_to_torappu_tree = {}
res_version_to_torappu_tree_parsed = {}


res_version_to_torappu_index_env = {}
res_version_to_torappu_index_tree = {}
res_version_to_torappu_index_tree_parsed = {}


def parse_torappu_tree(torappu_tree):
    ab_id_to_name = {}
    ab_name_to_id = {}

    ab_max_id = 0

    for i in torappu_tree["AssetBundleNames"]:
        ab_id_to_name[i[0]] = i[1]
        ab_name_to_id[i[1]] = i[0]
        ab_max_id = max(ab_max_id, i[0])

    ab_hash = {}
    ab_dep = {}

    for i in torappu_tree["AssetBundleInfos"]:
        ab_hash[ab_id_to_name[i[0]]] = i[1]["AssetBundleHash"]
        ab_dep[ab_id_to_name[i[0]]] = []
        for j in i[1]["AssetBundleDependencies"]:
            ab_dep[ab_id_to_name[i[0]]].append(ab_id_to_name[j])
    return ab_id_to_name, ab_name_to_id, ab_max_id, ab_hash, ab_dep


def parse_torappu_index_tree(torappu_index_tree):
    scc_id_to_ab_names = {}
    ab_name_to_scc_id = {}
    max_scc_id = 0
    abs = {}

    for i in torappu_index_tree["bundles"]:
        if i["sccIndex"] not in scc_id_to_ab_names:
            scc_id_to_ab_names[i["sccIndex"]] = set()
        scc_id_to_ab_names[i["sccIndex"]].add(i["name"])
        ab_name_to_scc_id[i["name"]] = i["sccIndex"]
        max_scc_id = max(max_scc_id, i["sccIndex"])
        abs[i["name"]] = i

    ab_name_to_as_names = {}

    for i in torappu_index_tree["assetToBundleList"]:
        if i["bundleName"] not in ab_name_to_as_names:
            ab_name_to_as_names[i["bundleName"]] = set()
        ab_name_to_as_names[i["bundleName"]].add(i["assetName"])

    return scc_id_to_ab_names, ab_name_to_scc_id, max_scc_id, abs, ab_name_to_as_names


def load_res_version(res_version):
    torappu_env = UnityPy.load(f"{res_version}/torappu.ab")
    res_version_to_torappu_env[res_version] = torappu_env

    for obj in torappu_env.objects:
        if obj.type.name == "AssetBundleManifest":
            torappu_tree = obj.read_typetree()
            with open(f"{res_version}/torappu.json", "w", encoding="utf-8") as f:
                json.dump(torappu_tree, f, ensure_ascii=False, indent=4)
            res_version_to_torappu_tree[res_version] = torappu_tree
            res_version_to_torappu_tree_parsed[res_version] = parse_torappu_tree(
                torappu_tree
            )

    torappu_index_env = UnityPy.load(f"{res_version}/torappu_index.ab")
    res_version_to_torappu_index_env[res_version] = torappu_index_env

    for obj in torappu_index_env.objects:
        if obj.type.name == "MonoBehaviour":
            torappu_index_tree = obj.read_typetree()
            with open(f"{res_version}/torappu_index.json", "w", encoding="utf-8") as f:
                json.dump(torappu_index_tree, f, ensure_ascii=False, indent=4)
            res_version_to_torappu_index_tree[res_version] = torappu_index_tree
            res_version_to_torappu_index_tree_parsed[res_version] = parse_torappu_index_tree(
                torappu_index_tree
            )


os.makedirs("tmp", exist_ok=True)

for source_version in legacy_source_versions:
    load_res_version(source_version)
for source_version in source_versions:
    load_res_version(source_version)
load_res_version(target_version)


target_scc_id_to_ab_names, target_ab_name_to_scc_id, target_max_scc_id, target_abs, target_ab_name_to_as_names = res_version_to_torappu_index_tree_parsed[
    target_version
]


new_abs = {}

for source_version in legacy_source_versions+source_versions:
    scc_id_to_ab_names, ab_name_to_scc_id, max_scc_id, abs, ab_name_to_as_names = res_version_to_torappu_index_tree_parsed[
        source_version
    ]
    for i in abs:
        if i not in target_abs and not i.startswith("gamedata/"):
            new_abs[i] = source_version

target_torappu_index_tree = res_version_to_torappu_index_tree[target_version]

for ab_name in new_abs:
    res_version = new_abs[ab_name]
    scc_id_to_ab_names, ab_name_to_scc_id, max_scc_id, abs, ab_name_to_as_names = res_version_to_torappu_index_tree_parsed[
        res_version
    ]
    ab = abs[ab_name]
    ab_names = scc_id_to_ab_names[ab_name_to_scc_id[ab_name]]
    scc_id = -1
    for i in ab_names:
        if i in target_abs:
            scc_id = target_ab_name_to_scc_id[i]
            break
    if scc_id == -1:
        target_max_scc_id += 1
        scc_id = target_max_scc_id
        target_scc_id_to_ab_names[scc_id] = set()
    ab["sccIndex"] = scc_id
    target_torappu_index_tree["bundles"].append(ab)
    target_scc_id_to_ab_names[scc_id].add(ab_name)
    target_ab_name_to_scc_id[ab_name] = scc_id
    target_abs[ab_name] = ab

    for as_name in ab_name_to_as_names[ab_name]:
        target_torappu_index_tree["assetToBundleList"].append(
            {
                "assetName": as_name,
                "bundleName": ab_name
            }
        )
        if as_name.startswith("activity/"):
            i = as_name.split('/')
            if len(i) == 4 and (i[2] == "zonemaps" or i[2] == "zonemap"):
                target_torappu_index_tree["assetToBundleList"].append(
                    {
                        "assetName": f"ui/zonemaps/{i[3]}",
                        "bundleName": ab_name
                    }
                )

levels = {}

for source_version in source_versions:
    scc_id_to_ab_names, ab_name_to_scc_id, max_scc_id, abs, ab_name_to_as_names = res_version_to_torappu_index_tree_parsed[
        source_version
    ]
    for i in ab_name_to_as_names["gamedata/levels/activities.ab"]:
        if i not in target_ab_name_to_as_names["gamedata/levels/activities.ab"]:
            levels[i] = source_version


for source_version in source_versions:
    scc_id_to_ab_names, ab_name_to_scc_id, max_scc_id, abs, ab_name_to_as_names = res_version_to_torappu_index_tree_parsed[
        source_version
    ]
    ab = abs["gamedata/levels/activities.ab"]
    ab["name"] = f"gamedata/levels/activities-{source_version}.ab"
    target_max_scc_id += 1
    ab["sccIndex"] = target_max_scc_id
    target_torappu_index_tree["bundles"].append(ab)

for level in levels:
    target_torappu_index_tree["assetToBundleList"].append(
        {
            "assetName": level,
            "bundleName": f"gamedata/levels/activities-{levels[level]}.ab"
        }
    )

for source_version in legacy_activities:
    legacy_activity = legacy_activities[source_version]
    scc_id_to_ab_names, ab_name_to_scc_id, max_scc_id, abs, ab_name_to_as_names = res_version_to_torappu_index_tree_parsed[
        source_version
    ]
    ab = abs[legacy_activity]
    ab["name"] = f"gamedata/levels/activities-{source_version}.ab"
    target_max_scc_id += 1
    ab["sccIndex"] = target_max_scc_id
    target_torappu_index_tree["bundles"].append(ab)
    for i in ab_name_to_as_names[legacy_activity]:
        target_torappu_index_tree["assetToBundleList"].append(
            {
                "assetName": i,
                "bundleName": f"gamedata/levels/activities-{source_version}.ab"
            }
        )


with open(f"tmp/torappu_index.json", "w", encoding="utf-8") as f:
    json.dump(target_torappu_index_tree, f, ensure_ascii=False, indent=4)


target_ab_id_to_name, target_ab_name_to_id, target_ab_max_id, target_ab_hash, target_ab_dep = res_version_to_torappu_tree_parsed[
    target_version
]

target_torappu_tree = res_version_to_torappu_tree[target_version]
for ab_name in new_abs:
    target_ab_max_id += 1
    ab_id = target_ab_max_id
    target_torappu_tree["AssetBundleNames"].append(
        [
            ab_id,
            ab_name
        ]
    )
    target_ab_id_to_name[ab_id] = ab_name
    target_ab_name_to_id[ab_name] = ab_id

for ab_name in new_abs:
    res_version = new_abs[ab_name]
    ab_id_to_name, ab_name_to_id, ab_max_id, ab_hash, ab_dep = res_version_to_torappu_tree_parsed[
        res_version
    ]
    if ab_name not in ab_name_to_id:
        continue
    ab_id = target_ab_name_to_id[ab_name]
    dep = []
    for i in ab_dep[ab_name]:
        if i in target_ab_name_to_id:
            dep.append(target_ab_name_to_id[i])
    target_torappu_tree["AssetBundleInfos"].append(
        [
            ab_id,
            {
                "AssetBundleHash": ab_hash[ab_name],
                "AssetBundleDependencies": dep
            }
        ]
    )

for source_version in source_versions:
    target_ab_max_id += 1
    target_torappu_tree["AssetBundleNames"].append(
        [
            target_ab_max_id,
            f"gamedata/levels/activities-{source_version}.ab"
        ]
    )
    ab_id_to_name, ab_name_to_id, ab_max_id, ab_hash, ab_dep = res_version_to_torappu_tree_parsed[
        source_version
    ]
    target_torappu_tree["AssetBundleInfos"].append(
        [
            target_ab_max_id,
            {
                "AssetBundleHash": ab_hash["gamedata/levels/activities.ab"],
                "AssetBundleDependencies": []
            }
        ]
    )

for source_version in legacy_activities:
    legacy_activity = legacy_activities[source_version]
    target_ab_max_id += 1
    target_torappu_tree["AssetBundleNames"].append(
        [
            target_ab_max_id,
            f"gamedata/levels/activities-{source_version}.ab"
        ]
    )
    ab_id_to_name, ab_name_to_id, ab_max_id, ab_hash, ab_dep = res_version_to_torappu_tree_parsed[
        source_version
    ]
    target_torappu_tree["AssetBundleInfos"].append(
        [
            target_ab_max_id,
            {
                "AssetBundleHash": ab_hash[legacy_activity],
                "AssetBundleDependencies": []
            }
        ]
    )

with open(f"tmp/torappu.json", "w", encoding="utf-8") as f:
    json.dump(target_torappu_tree, f, ensure_ascii=False, indent=4)


target_torappu_env = res_version_to_torappu_env[target_version]
for obj in target_torappu_env.objects:
    if obj.type.name == "AssetBundleManifest":
        obj.save_typetree(target_torappu_tree)

with open("tmp/torappu.ab", "wb") as f:
    f.write(target_torappu_env.file.save())


target_torappu_index_env = res_version_to_torappu_index_env[target_version]
for obj in target_torappu_index_env.objects:
    if obj.type.name == "MonoBehaviour":
        obj.save_typetree(target_torappu_index_tree)

with open("tmp/torappu_index.ab", "wb") as f:
    f.write(target_torappu_index_env.file.save())


if shutil.which("flatc") is None:
    flatc_url = "https://github.com/google/flatbuffers/releases/download/v23.5.26/Windows.flatc.binary.zip"
    r = requests.get(
        "https://api.github.com/repos/google/flatbuffers/releases/latest"
    )
    s = r.json()
    for i in s["assets"]:
        if i["name"].find("flatc") != -1 and i["name"].endswith(".zip") and i["name"].find("Windows") != -1:
            flatc_url = i["browser_download_url"]
            break
    flatc_file_name = os.path.basename(flatc_url)
    if not os.path.exists(flatc_file_name):
        print("Download:", flatc_file_name)
        subprocess.run(
            [
                "curl", "-L", "-O", flatc_url
            ]
        )
    print("Use:", flatc_file_name)
    with ZipFile(flatc_file_name) as f:
        f.extractall()


def process_level(level):
    if "enemyDbRefs" in level and level["enemyDbRefs"] is not None:
        for j in level["enemyDbRefs"]:
            if "overwrittenData" in j and j["overwrittenData"] is not None:
                if "attributes" in j["overwrittenData"] and j["overwrittenData"]["attributes"] is not None:
                    for k in ["epDamageResistance", "epResistance", "damageHitratePhysical", "damageHitrateMagical", "disarmedCombatImmune"]:
                        if k not in j["overwrittenData"]["attributes"]:
                            j["overwrittenData"]["attributes"][k] = {}
                for k in ["applyWay", "motion", "enemyTags", "notCountInTotal"]:
                    if k not in j["overwrittenData"]:
                        j["overwrittenData"][k] = {}


for source_version in source_versions:
    os.makedirs(f"tmp/{source_version}/0/", exist_ok=True)
    os.makedirs(f"tmp/{source_version}/1/", exist_ok=True)
    os.makedirs(f"tmp/{source_version}/2/", exist_ok=True)

    filelist = []

    activities_env = UnityPy.load(
        f"{source_version}/gamedata/levels/activities.ab"
    )
    for obj in activities_env.objects:
        if obj.type.name == "TextAsset":
            data = obj.read()
            with open(f"tmp/{source_version}/0/{data.name}", "wb") as f:
                f.write(bytes(data.script)[128:])
            filelist.append(data.name)

    subprocess.run(
        [
            "flatc",
            "--json", "--raw-binary",
            "-o", f"tmp/{source_version}/1/",
            "--strict-json", "--natural-utf8",
            f"fbs/{source_version}/prts___levels.fbs",
            "--",
            *[f"tmp/{source_version}/0/{i}" for i in filelist]
        ]
    )

    for i in filelist:
        with open(f"tmp/{source_version}/1/{i}.json", encoding="utf-8") as f:
            level = json.load(f)

        process_level(level)

        with open(f"tmp/{source_version}/1/{i}.json", "w", encoding="utf-8") as f:
            json.dump(level, f, ensure_ascii=False, indent=4)

    subprocess.run(
        [
            "flatc",
            "--binary",
            "-o", f"tmp/{source_version}/2/",
            "--strict-json", "--natural-utf8",
            "fbs/target_version/prts___levels.fbs",
            *[f"tmp/{source_version}/1/{i}.json" for i in filelist]
        ]
    )

    for obj in activities_env.objects:
        if obj.type.name == "TextAsset":
            data = obj.read()
            with open(f"tmp/{source_version}/2/{data.name}.bin", "rb") as f:
                data.script = bytes(128) + f.read()
            data.save()
    with open(f"tmp/activities-{source_version}.ab", "wb") as f:
        f.write(activities_env.file.save())


for source_version in legacy_activities:
    legacy_activity = legacy_activities[source_version]
    os.makedirs(f"tmp/{source_version}/1/", exist_ok=True)
    os.makedirs(f"tmp/{source_version}/2/", exist_ok=True)

    filelist = []

    activities_env = UnityPy.load(
        f"{source_version}/{legacy_activity}"
    )
    for obj in activities_env.objects:
        if obj.type.name == "TextAsset":
            data = obj.read()
            with open(f"tmp/{source_version}/1/{data.name}.json", "w", encoding="utf-8") as f:
                json.dump(
                    bson.loads(
                        bytes(data.script)[128:]),
                    f, ensure_ascii=False, indent=4
                )
            filelist.append(data.name)

    for i in filelist:
        with open(f"tmp/{source_version}/1/{i}.json", encoding="utf-8") as f:
            level = json.load(f)

        if "mapData" in level and level["mapData"] is not None:
            if "map" in level["mapData"] and level["mapData"]["map"] is not None:
                row_size = len(level["mapData"]["map"])
                column_size = len(level["mapData"]["map"][0])
                matrix_data = []
                for j in level["mapData"]["map"]:
                    matrix_data += j
                level["mapData"]["map"] = {
                    "row_size": row_size,
                    "column_size": column_size,
                    "matrix_data": matrix_data
                }
            if "width" in level["mapData"]:
                del level["mapData"]["width"]
            if "height" in level["mapData"]:
                del level["mapData"]["height"]

        if "waves" in level and level["waves"] is not None:
            for j in level["waves"]:
                if "fragments" in j and j["fragments"] is not None:
                    for k in j["fragments"]:
                        if "name" in k:
                            del k["name"]
                if "name" in j:
                    del j["name"]
        if "routes" in level and level["routes"] is not None:
            for j in range(len(level["routes"])):
                if level["routes"][j] is None:
                    level["routes"][j] = {
                        "motionMode": "E_NUM",
                        "startPosition": {},
                        "endPosition": {},
                        "spawnRandomRange": {},
                        "spawnOffset": {},
                        "allowDiagonalMove": True
                    }
        if "extraRoutes" in level and level["extraRoutes"] is not None:
            for j in range(len(level["extraRoutes"])):
                if level["extraRoutes"][j] is None:
                    level["extraRoutes"][j] = {
                        "motionMode": "E_NUM",
                        "startPosition": {},
                        "endPosition": {},
                        "spawnRandomRange": {},
                        "spawnOffset": {},
                        "allowDiagonalMove": True
                    }

        if "branches" in level and level["branches"] is not None:
            branches = [
                {
                    "key": j,
                    "value": level["branches"][j]
                } for j in level["branches"]
            ]
            level["branches"] = branches

        process_level(level)

        with open(f"tmp/{source_version}/1/{i}.json", "w", encoding="utf-8") as f:
            json.dump(level, f, ensure_ascii=False, indent=4)

    subprocess.run(
        [
            "flatc",
            "--binary",
            "-o", f"tmp/{source_version}/2/",
            "--strict-json", "--natural-utf8",
            "fbs/target_version/prts___levels.fbs",
            *[f"tmp/{source_version}/1/{i}.json" for i in filelist]
        ]
    )

    for obj in activities_env.objects:
        if obj.type.name == "TextAsset":
            data = obj.read()
            with open(f"tmp/{source_version}/2/{data.name}.bin", "rb") as f:
                data.script = bytes(128) + f.read()
            data.save()
    with open(f"tmp/activities-{source_version}.ab", "wb") as f:
        f.write(activities_env.file.save())

os.makedirs("mod", exist_ok=True)

with ZipFile("mod/mod.dat", "w") as f:
    f.write("tmp/torappu.ab", "torappu.ab")
    f.write("tmp/torappu_index.ab", "torappu_index.ab")
    for source_version in source_versions:
        f.write(
            f"tmp/activities-{source_version}.ab",
            f"gamedata/levels/activities-{source_version}.ab"
        )
    for source_version in legacy_activities:
        f.write(
            f"tmp/activities-{source_version}.ab",
            f"gamedata/levels/activities-{source_version}.ab"
        )

with open("mod.txt", "w") as f:
    for ab_name in new_abs:
        res_version = new_abs[ab_name]
        filename = os.path.splitext(
            ab_name.replace(
                '/', '_'
            ).replace(
                '#', "__"
            )
        )[0]+".dat"
        print(
            f"https://ak.hycdn.cn/assetbundle/official/Android/assets/{res_version}/{filename}",
            file=f
        )

if shutil.which("aria2c") is None:
    aria2_url = "https://github.com/aria2/aria2/releases/download/release-1.37.0/aria2-1.37.0-win-64bit-build1.zip"
    r = requests.get(
        "https://api.github.com/repos/aria2/aria2/releases/latest"
    )
    s = r.json()
    for i in s["assets"]:
        if i["name"].startswith("aria2") and i["name"].endswith(".zip") and i["name"].find("win-64bit") != -1:
            aria2_url = i["browser_download_url"]
            break
    aria2_file_name = os.path.basename(aria2_url)
    if not os.path.exists(aria2_file_name):
        print("Download:", aria2_file_name)
        subprocess.run(
            [
                "curl", "-L", "-O", aria2_url
            ]
        )
    print("Use:", aria2_file_name)
    with ZipFile(aria2_file_name) as f:
        aria2_namelist = f.namelist()
        for name in aria2_namelist:
            if name.endswith("aria2c.exe"):
                with open("aria2c.exe", "wb") as fout:
                    fout.write(f.read(name))
                    break

subprocess.run(
    [
        "aria2c",
        "--allow-overwrite",
        "-d", f"mod",
        "-i", "mod.txt"
    ]
)
