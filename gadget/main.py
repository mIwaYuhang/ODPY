import requests
import subprocess
import os
import lzma
import shutil
import json
from zipfile import ZipFile

with open("settings.json") as f:
    settings = json.load(f)

IS_GLOBAL = settings["isGlobal"]

IS_DEV_APK = settings["isDevApk"]

GLOBAL_XAPK_FILENAME = settings["globalXapkFilename"]


print("---Prepare---")

if IS_GLOBAL:
    if not os.path.isfile(GLOBAL_XAPK_FILENAME):
        print(
            "Err:", GLOBAL_XAPK_FILENAME,
            "not found, please download it manually from https://apkpure.net/arknights/com.YoStarEN.Arknights"
        )
        exit(1)

    if os.path.exists("global"):
        shutil.rmtree("global")

    os.makedirs("global", exist_ok=True)

    with ZipFile(GLOBAL_XAPK_FILENAME) as f:
        f.extractall("global")

    for i in os.listdir("global/Android/obb/com.YoStarEN.Arknights"):
        if i.find("com.YoStarEN.Arknights") != -1:
            j = i.replace(
                "com.YoStarEN.Arknights",
                "com.odpy.global.Arknights"
            )
            shutil.move(
                f"global/Android/obb/com.YoStarEN.Arknights/{i}",
                f"global/Android/obb/com.YoStarEN.Arknights/{j}"
            )

    shutil.move(
        "global/Android/obb/com.YoStarEN.Arknights",
        "global/Android/obb/com.odpy.global.Arknights"
    )

    shutil.move(
        "global/com.YoStarEN.Arknights.apk",
        "com.YoStarEN.Arknights.apk"
    )


if IS_GLOBAL:
    game_file_name = "com.YoStarEN.Arknights.apk"
else:
    r = requests.head(
        "https://ak.hypergryph.com/downloads/android_lastest"
    )
    game_url = r.headers.get("location")
    game_base_url = os.path.dirname(game_url)
    game_file_name = os.path.basename(game_url)

    alt_game_file_name = game_file_name.replace(
        "arknights-hg-", "arknights-backup-328-", 1
    )
    alt_game_url = f"{game_base_url}/{alt_game_file_name}"

    if not os.path.exists(alt_game_file_name) and not os.path.exists(game_file_name):
        r = requests.head(
            alt_game_url
        )
        if r.status_code == 200:
            game_url = alt_game_url
            game_file_name = alt_game_file_name
        print("Download:", game_file_name)
        subprocess.run(
            [
                "curl", "-L", "-O", game_url
            ]
        )
    else:
        if os.path.exists(alt_game_file_name):
            game_file_name = alt_game_file_name

print("Use:", game_file_name)

apktool_url = "https://github.com/iBotPeaches/Apktool/releases/download/v2.9.1/apktool_2.9.1.jar"
r = requests.get(
    "https://api.github.com/repos/iBotPeaches/Apktool/releases/latest"
)
s = r.json()
for i in s["assets"]:
    if i["name"].startswith("apktool") and i["name"].endswith(".jar"):
        apktool_url = i["browser_download_url"]
        break

apktool_file_name = os.path.basename(apktool_url)
if not os.path.exists(apktool_file_name):
    print("Download:", apktool_file_name)
    subprocess.run(
        [
            "curl", "-L", "-O", apktool_url
        ]
    )
print("Use:", apktool_file_name)


apk_signer_url = "https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar"
r = requests.get(
    "https://api.github.com/repos/patrickfav/uber-apk-signer/releases/latest"
)
s = r.json()
for i in s["assets"]:
    if i["name"].startswith("uber-apk-signer") and i["name"].endswith(".jar"):
        apk_signer_url = i["browser_download_url"]
        break

apk_signer_file_name = os.path.basename(apk_signer_url)
if not os.path.exists(apk_signer_file_name):
    print("Download:", apk_signer_file_name)
    subprocess.run(
        [
            "curl", "-L", "-O", apk_signer_url
        ]
    )
print("Use:", apk_signer_file_name)

r = requests.get("https://api.github.com/repos/frida/frida/releases/latest")
s = r.json()
frida_version = s["tag_name"]
for architecture in ["x86", "arm64", "arm"]:
    frida_gadget_file_name = f"frida-gadget-{frida_version}-android-{architecture}.so"
    if not os.path.exists(frida_gadget_file_name):
        print("Download:", f"{frida_gadget_file_name}.xz")
        frida_gadget_url = f"https://github.com/frida/frida/releases/download/{frida_version}/{frida_gadget_file_name}.xz"
        subprocess.run(
            [
                "curl", "-L", "-O", frida_gadget_url
            ]
        )
        print("Use:", f"{frida_gadget_file_name}.xz")
        with lzma.open(f"{frida_gadget_file_name}.xz") as f, open(frida_gadget_file_name, "wb") as fout:
            fout.write(f.read())
    print("Use:", frida_gadget_file_name)


keytool_file_name = "keytool"
if shutil.which(keytool_file_name) is None:
    print("Warn:", '"keytool" not found in path')
    keytool_found = False
    for i in range(21, 17-1, -1):
        keytool_file_name = f"C:\\Program Files\\Java\\jdk-{i}\\bin\\keytool.exe"
        if os.path.exists(keytool_file_name):
            keytool_found = True
            break
    if not keytool_found:
        print('"keytool" not found anywhere')
        exit(1)
print("Use:", keytool_file_name)

keystore_file_name = "arknights.keystore"
if not os.path.exists(keystore_file_name):
    print("Generate:", keystore_file_name)
    subprocess.run(
        [
            keytool_file_name, "-genkeypair",
            "-keyalg", "RSA",
            "-alias", "ak",
            "-dname", "CN=arknights",
            "-validity", "36500",
            "-keystore", keystore_file_name,
            "-storepass", "123456",
            "-keypass", "123456"
        ]
    )
print("Use:", keystore_file_name)


game_folder_name = os.path.splitext(game_file_name)[0]

if os.path.exists(game_folder_name):
    shutil.rmtree(game_folder_name)

print("---Decode---")

subprocess.run(
    [
        "java", "-jar", apktool_file_name, "d", game_file_name
    ]
)

print("---Inject---")


with open(f"{game_folder_name}/AndroidManifest.xml") as f:
    android_manifest = f.read()

if IS_GLOBAL:
    android_manifest = android_manifest.replace(
        'package="com.YoStarEN.Arknights"',
        'package="com.odpy.global.Arknights"', 1
    )
else:
    android_manifest = android_manifest.replace(
        'package="com.hypergryph.arknights"',
        'package="com.odpy.arknights"', 1
    )

if not IS_GLOBAL:
    android_manifest = android_manifest.replace(
        '<application',
        '<application android:requestLegacyExternalStorage="true"', 1
    )

target_1 = '<uses-permission'
target_2 = '/>'

index = android_manifest.find(
    target_2, android_manifest.rfind(target_1)
)+len(target_2)

android_manifest = android_manifest[:index]+"""
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
<uses-permission android:name="android.permission.MANAGE_EXTERNAL_STORAGE"/>"""+android_manifest[index:]

android_manifest = android_manifest.replace(
    "com.hypergryph.arknights.hgShareProvider",
    "com.odpy.arknights.hgShareProvider"
)

android_manifest = android_manifest.replace(
    "com.hypergryph.arknights.share-to-follow-file-provider",
    "com.odpy.arknights.share-to-follow-file-provider"
)

android_manifest = android_manifest.replace(
    "com.hypergryph.arknights.fileprovider",
    "com.odpy.arknights.fileprovider"
)


android_manifest = android_manifest.replace(
    "com.YoStarEN.Arknights.firebaseinitprovider",
    "com.odpy.global.Arknights.firebaseinitprovider"
)

android_manifest = android_manifest.replace(
    "com.YoStarEN.Arknights.fileprovider",
    "com.odpy.global.Arknights.fileprovider"
)

android_manifest = android_manifest.replace(
    "com.YoStarEN.Arknights.sls_provider",
    "com.odpy.global.Arknights.sls_provider"
)

android_manifest = android_manifest.replace(
    "com.YoStarEN.Arknights.FacebookInitProvider",
    "com.odpy.global.Arknights.FacebookInitProvider"
)

android_manifest = android_manifest.replace(
    "com.YoStarEN.Arknights.playgamesinitprovider",
    "com.odpy.global.Arknights.playgamesinitprovider"
)

android_manifest = android_manifest.replace(
    "com.YoStarEN.Arknights.permission.C2D_MESSAGE",
    "com.odpy.global.Arknights.permission.C2D_MESSAGE"
)


with open(f"{game_folder_name}/AndroidManifest.xml", "w") as f:
    f.write(android_manifest)

with open(f"{game_folder_name}/smali/com/u8/sdk/U8UnityContext.smali") as f:
    smali = f.read()

target_1 = "<clinit>"
target_2 = ".locals"
target_3 = '\n'

if IS_GLOBAL:
    index = smali.find(
        target_1
    )
    smali = smali[:index]+smali[index:].replace(".locals 0", ".locals 1", 1)

index = smali.find(
    target_3,
    smali.find(
        target_2,
        smali.find(
            target_1
        )
    )
)+len(target_3)

smali = smali[:index]+"""
const-string v0, "frida-gadget"
invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
"""+smali[index:]

with open(f"{game_folder_name}/smali/com/u8/sdk/U8UnityContext.smali", "w") as f:
    f.write(smali)

if IS_GLOBAL:
    with open(f"{game_folder_name}/res/values/strings.xml", encoding="utf-8") as f:
        strings = f.read()

    strings = strings.replace(
        '<string name="app_name">Arknights</string>',
        '<string name="app_name">ODPY-GLOBAL-DEV</string>' if IS_DEV_APK else '<string name="app_name">ODPY-GLOBAL</string>', 1
    )

    with open(f"{game_folder_name}/res/values/strings.xml", "w", encoding="utf-8") as f:
        f.write(strings)
else:
    with open(f"{game_folder_name}/res/values-zh/strings.xml", encoding="utf-8") as f:
        strings = f.read()

    strings = strings.replace("明日方舟", "ODPY-DEV" if IS_DEV_APK else "ODPY", 1)

    with open(f"{game_folder_name}/res/values-zh/strings.xml", "w", encoding="utf-8") as f:
        f.write(strings)

for architecture, architecture_folder_name in [("x86", "x86"), ("arm64", "arm64-v8a"), ("arm", "armeabi-v7a")]:
    frida_gadget_file_name = f"frida-gadget-{frida_version}-android-{architecture}.so"
    if os.path.isdir(f"{game_folder_name}/lib/{architecture_folder_name}"):
        shutil.copyfile(
            frida_gadget_file_name,
            f"{game_folder_name}/lib/{architecture_folder_name}/libfrida-gadget.so"
        )
        if not IS_DEV_APK:
            shutil.copyfile(
                "libfrida-gadget.config.so",
                f"{game_folder_name}/lib/{architecture_folder_name}/libfrida-gadget.config.so"
            )

print("---Build---")

subprocess.run(
    [
        "java", "-jar", apktool_file_name, "b", game_folder_name
    ]
)

print("---Sign---")

subprocess.run(
    [
        "java", "-jar", apk_signer_file_name,
        "-a", f"{game_folder_name}/dist/{game_file_name}",
        "--ks", keystore_file_name,
        "--ksAlias", "ak",
        "--ksPass", "123456",
        "--ksKeyPass", "123456",
    ]
)

odpy_apk_name = "odpy.apk"

if IS_DEV_APK:
    odpy_apk_name = "odpy-dev.apk"

shutil.move(
    f"{game_folder_name}/dist/{game_folder_name}-aligned-signed.apk", odpy_apk_name
)

if IS_GLOBAL:
    print("---XAPK---")
    odpy_xapk_name = "odpy.xapk"
    if IS_DEV_APK:
        odpy_xapk_name = "odpy-dev.xapk"
    shutil.copyfile(odpy_apk_name, "global/com.odpy.global.Arknights.apk")
    shutil.make_archive("odpy", "zip", "global")
    shutil.move("odpy.zip", odpy_xapk_name)
