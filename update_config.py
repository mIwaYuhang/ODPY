import requests
import json

with open("config/config.json") as f:
    config = json.load(f)

for i, j, k, l in [
    [
        "version", "cn",
        "ak-conf.hypergryph.com",
        "https://ak-conf.hypergryph.com/config/prod/official/Android/version"
    ],
    [
        "versionGlobal", "global",
        "ak-conf.arknights.global",
        "https://ark-us-static-online.yo-star.com/assetbundle/official/Android/version"
    ]
]:

    old_resVersion = config[i]["android"]["resVersion"]
    old_clientVersion = config[i]["android"]["clientVersion"]

    old_funcVer = config["networkConfig"][j]["content"]["funcVer"]

    timeout = 30

    try:
        version = requests.get(
            l, timeout=timeout
        ).json()
        resVersion = version["resVersion"]
        clientVersion = version["clientVersion"]
        if resVersion != old_resVersion:
            config[i]["android"]["resVersion"] = resVersion
        if clientVersion != old_clientVersion:
            config[i]["android"]["clientVersion"] = clientVersion

    except Exception:
        pass

    try:
        network_config = requests.get(
            f"https://{k}/config/prod/official/network_config", timeout=timeout
        ).json()
        content = json.loads(network_config["content"])
        funcVer = content["funcVer"]
        if funcVer != old_funcVer:
            config["networkConfig"][j]["content"]["funcVer"] = funcVer
            config["networkConfig"][j]["content"]["configs"][funcVer] = config["networkConfig"][j]["content"]["configs"][old_funcVer]
            del config["networkConfig"][j]["content"]["configs"][old_funcVer]

    except Exception:
        pass


with open("config/config.json", "w") as f:
    json.dump(config, f, indent=4)
