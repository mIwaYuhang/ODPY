import json
from collections import OrderedDict
import os

for legacy_cc_name in os.listdir("data/crisis/"):
    with open("data/crisisV2/cc1.json", encoding="utf-8") as f:
        template = json.load(f)

    for i in template["info"]["mapStageDataMap"]:
        if template["info"]["mapStageDataMap"][i]["stageType"] == "PERMANENT":
            template_map_id = template["info"]["mapStageDataMap"][i]["mapId"]
            break

    with open(f"data/crisis/{legacy_cc_name}", encoding="utf-8") as f:
        target = json.load(f)

    for i in target["data"]["seasonInfo"][0]["stages"]:
        if target["data"]["seasonInfo"][0]["stages"][i]["type"] == "PERMANENT":
            target_stage_id = target["data"]["seasonInfo"][0]["stages"][i]["stageId"]
            break

    template["info"]["mapStageDataMap"][template_map_id]["stageId"] = target["data"]["seasonInfo"][0]["stages"][target_stage_id]["stageId"]
    template["info"]["mapStageDataMap"][template_map_id]["levelId"] = target["data"]["seasonInfo"][0]["stages"][target_stage_id]["levelId"]
    template["info"]["mapStageDataMap"][template_map_id]["mapId"] = target["data"]["seasonInfo"][0]["stages"][target_stage_id]["mapId"]
    template["info"]["mapStageDataMap"][template_map_id]["code"] = target["data"]["seasonInfo"][0]["stages"][target_stage_id]["code"]
    template["info"]["mapStageDataMap"][template_map_id]["name"] = target["data"]["seasonInfo"][0]["stages"][target_stage_id]["name"]
    template["info"]["mapStageDataMap"][template_map_id]["loadingPicId"] = target[
        "data"]["seasonInfo"][0]["stages"][target_stage_id]["loadingPicId"]
    template["info"]["mapStageDataMap"][template_map_id]["description"] = target[
        "data"]["seasonInfo"][0]["stages"][target_stage_id]["description"]
    # template["info"]["mapStageDataMap"][template_map_id]["picId"] = target["data"]["seasonInfo"][0]["stages"][target_stage_id]["picId"]
    template["info"]["mapStageDataMap"][template_map_id]["logoPicId"] = target["data"]["seasonInfo"][0]["stages"][target_stage_id]["logoPicId"]

    template["info"]["mapDetailDataMap"][template_map_id]["groupDescDataMap"] = {}
    template["info"]["mapDetailDataMap"][template_map_id]["roadRelationDataMap"] = {}
    template["info"]["mapDetailDataMap"][template_map_id]["bagRoadDataMap"] = {}

    template["info"]["mapDetailDataMap"][template_map_id]["nodeViewData"] = {
        "width": 1000,
        "height": 400,
        "bagPosMap": {},
        "roadPosMap": {},
        "nodePosMap": {
            "node_0": {
                "position": {
                    "x": 0,
                    "y": 0
                }
            }
        },
        "exclusionDataMap": {}
    }
    template["info"]["mapDetailDataMap"][template_map_id]["bagViewData"] = {
        "width": 1000,
        "height": 400,
        "treasurePosMap": {},
        "bagPosMap": {},
        "roadPosMap": {}
    }

    template["info"]["mapDetailDataMap"][template_map_id]["bagDataMap"] = {}
    template["info"]["mapDetailDataMap"][template_map_id]["exclusionDataMap"] = {}
    template["info"]["mapDetailDataMap"][template_map_id]["nodeDataMap"] = {
        "node_0": {
            "runeId": None,
            "slotPackId": None,
            "nodeType": "START",
            "mutualExclusionGroup": None,
            "adjacentNodeList": []
        }
    }
    template["info"]["mapDetailDataMap"][template_map_id]["runeDataMap"] = {}

    rune_names = {}
    for i in target["data"]["runeInfoList"][target_stage_id]:
        rune_names[i["runeId"]] = i["runeName"]

    pack_nodes = OrderedDict()

    num_pack = 0
    num_rune = 0
    for i in target["data"]["stageRune"][target_stage_id]:
        rune_id = i
        rune_group_id = "group_" + i
        node_id = "node_" + i
        if target["data"]["stageRune"][target_stage_id][i]["mutexGroupKey"]:
            pack_id = "pack_" + \
                target["data"]["stageRune"][target_stage_id][i]["mutexGroupKey"]
            exclude_id = "exclude_" + \
                target["data"]["stageRune"][target_stage_id][i]["mutexGroupKey"]
        else:
            pack_id = "pack_" + i
            exclude_id = None
        if pack_id not in template["info"]["mapDetailDataMap"][template_map_id]["bagDataMap"]:
            num_pack += 1
            template["info"]["mapDetailDataMap"][template_map_id]["bagDataMap"][pack_id] = {
                "slotPackId": pack_id,
                "slotPackType": "HIGHEST_TOTAL_SCORE",
                "mapId": target_stage_id,
                "mapSlotId": None,
                "slotPackName": pack_id,
                "slotPackFullName": pack_id,
                "isDaily": False,
                "dimension": 0,
                "previewTitle": pack_id,
                "previewDesc": pack_id,
                "rewardScore": 0,
                "sortId": num_pack,
                "missionSortId": num_pack,
                "slotPackRewards": []
            }
            pack_nodes[pack_id] = []
        pack_nodes[pack_id].append(node_id)
        if exclude_id is not None:
            if exclude_id not in template["info"]["mapDetailDataMap"][template_map_id]["exclusionDataMap"]:
                template["info"]["mapDetailDataMap"][template_map_id]["exclusionDataMap"][exclude_id] = {
                    "defaultSlotId": node_id
                }
        template["info"]["mapDetailDataMap"][template_map_id]["nodeDataMap"][node_id] = {
            "runeId": rune_id,
            "slotPackId": pack_id,
            "nodeType": "NORMAL",
            "mutualExclusionGroup": exclude_id,
            "adjacentNodeList": [
                "node_0"
            ]
        }

        num_rune += 1
        template["info"]["mapDetailDataMap"][template_map_id]["runeDataMap"][rune_id] = {
            "runeId": rune_id,
            "runeGroupId": rune_group_id,
            "runeIcon": f'g_enemy_atk_{target["data"]["stageRune"][target_stage_id][i]["points"]}',
            "runeName": rune_names[rune_id],
            "score": target["data"]["stageRune"][target_stage_id][i]["points"],
            "dimension": 0,
            "packedRune": {
                "id": rune_id,
                "points": 0,
                "mutexGroupKey": target["data"]["stageRune"][target_stage_id][i]["mutexGroupKey"],
                "description": target["data"]["stageRune"][target_stage_id][i]["description"],
                "runes": target["data"]["stageRune"][target_stage_id][i]["runes"]
            },
            "sortId": num_rune
        }
        template["info"]["mapDetailDataMap"][template_map_id]["groupDescDataMap"][rune_group_id] = {
            "desc": target["data"]["stageRune"][target_stage_id][i]["description"],
            "sortId": num_rune
        }
        template["info"]["mapDetailDataMap"][template_map_id]["nodeDataMap"]["node_0"]["adjacentNodeList"].append(
            node_id
        )

    for pack_id in pack_nodes:
        pack_nodes[pack_id].sort(
            key=lambda i: template["info"]
            ["mapDetailDataMap"][template_map_id]["runeDataMap"][i[5:]]["score"]
        )

    for exclude_id in template["info"]["mapDetailDataMap"][template_map_id]["exclusionDataMap"]:
        template["info"]["mapDetailDataMap"][template_map_id]["exclusionDataMap"][
            exclude_id]["defaultSlotId"] = pack_nodes["pack_"+exclude_id[8:]][-1]

    for i, pack_id in enumerate(pack_nodes):
        template["info"]["mapDetailDataMap"][template_map_id]["bagViewData"]["height"] += 200
        template["info"]["mapDetailDataMap"][template_map_id]["bagViewData"]["bagPosMap"][pack_id] = {
            "pos": {
                "x": 500,
                "y": -200-200*i
            },
            "size": {
                "x": 600,
                "y": 100
            }
        }
        template["info"]["mapDetailDataMap"][template_map_id]["nodeViewData"]["height"] += 200
        template["info"]["mapDetailDataMap"][template_map_id]["nodeViewData"]["bagPosMap"][pack_id] = {
            "pos": {
                "x": 500,
                "y": -120-200*i
            },
            "size": {
                "x": 800,
                "y": 100
            }
        }
        for j, node_id in enumerate(pack_nodes[pack_id]):
            template["info"]["mapDetailDataMap"][template_map_id]["nodeViewData"]["nodePosMap"][node_id] = {
                "position": {
                    "x": 200+100*j,
                    "y": -200-200*i
                }
            }

    template["info"]["mapStageDataMap"][target_stage_id] = template["info"]["mapStageDataMap"][template_map_id]
    del template["info"]["mapStageDataMap"][template_map_id]

    template["info"]["mapDetailDataMap"][target_stage_id] = template["info"]["mapDetailDataMap"][template_map_id]
    del template["info"]["mapDetailDataMap"][template_map_id]

    with open(f"data/crisisV2/legacy-{legacy_cc_name}", "w", encoding="utf-8") as f:
        json.dump(template, f, ensure_ascii=False, indent=4)
