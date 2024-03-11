from flask import request
from werkzeug.utils import safe_join

from constants import GACHA_JSON_PATH, POOL_JSON_PATH, POOL_CLASSIC_JSON_PATH, GACHA_TEMP_JSON_PATH, CONFIG_PATH, GACHA_UP_CHAR_JSON_PATH, GACHA_TABLE_URL, POOL_JSON_DIR
from utils import read_json, write_json, decrypt_battle_data
from core.function.update import updateData
import random
import os

from faketime import time


def normalGacha():
    request_json = request.json
    start_ts = int(time())
    return {
        "playerDataDelta": {
            "modified": {
                "recruit": {
                    "normal": {
                        "slots": {
                            str(request_json["slotId"]): {
                                "state": 2,
                                "selectTags": [
                                    {
                                        "tagId": i,
                                        "pick": 1
                                    } for i in request_json["tagList"]
                                ],
                                "startTs": start_ts,
                                "durationInSec": request_json["duration"],
                                "maxFinishTs": start_ts+request_json["duration"],
                                "realFinishTs": start_ts+request_json["duration"]
                            }
                        }
                    }
                }
            },
            "deleted": {}
        }
    }


def boostNormalGacha():
    request_json = request.json
    real_finish_ts = int(time())
    return {
        "playerDataDelta": {
            "modified": {
                "recruit": {
                    "normal": {
                        "slots": {
                            str(request_json["slotId"]): {
                                "state": 3,
                                "realFinishTs": real_finish_ts
                            }
                        }
                    }
                }
            },
            "deleted": {}
        }
    }


def finishNormalGacha():
    request_json = request.json
    gacha = read_json(GACHA_JSON_PATH)
    char_id = gacha["normal"]["charId"]
    char_inst_id = int(char_id.split('_')[1])
    is_new = gacha["normal"]["isNew"]
    return {
        "result": 0,
        "charGet": {
            "charInstId": char_inst_id,
            "charId": char_id,
            "isNew": is_new,
            "itemGet": [
                {
                    "type": "HGG_SHD",
                    "id": "4004",
                    "count": 999

                },
                {
                    "type": "LGG_SHD",
                    "id": "4005",
                    "count": 999
                },
                {
                    "type": "MATERIAL",
                    "id": f"p_{char_id}",
                    "count": 999
                }
            ],
            "logInfo": {}
        },
        "playerDataDelta": {
            "modified": {
                "recruit": {
                    "normal": {
                        "slots": {
                            str(request_json["slotId"]): {
                                "state": 1,
                                "selectTags": [],
                                "startTs": -1,
                                "durationInSec": -1,
                                "maxFinishTs": -1,
                                "realFinishTs": -1
                            }
                        }
                    }
                }
            },
            "deleted": {}
        }
    }


def syncNormalGacha():
    return {
        "playerDataDelta": {
            "modified": {},
            "deleted": {}
        }
    }


def doGetPool(poolId):
    gacha_table = updateData(GACHA_TABLE_URL)
    is_valid = False
    for i in gacha_table["gachaPoolClient"]:
        if i["gachaPoolId"] == poolId:
            is_valid = True
    for i in gacha_table["newbeeGachaPoolClient"]:
        if i["gachaPoolId"] == poolId:
            is_valid = True
    if is_valid:
        pool_file = safe_join(POOL_JSON_DIR, poolId+".json")
        if os.path.isfile(pool_file):
            pool = read_json(pool_file, encoding="utf-8")
            return pool
    if poolId.startswith("CLASSIC_"):
        pool = read_json(POOL_CLASSIC_JSON_PATH, encoding="utf-8")
    else:
        pool = read_json(POOL_JSON_PATH, encoding="utf-8")
    return pool


def doWishes(num, poolId):
    chars = []
    pool = doGetPool(poolId)
    rankChars = {}
    rankProb = {}
    for i in pool["detailInfo"]["availCharInfo"]["perAvailList"]:
        rankChars[i["rarityRank"]] = i["charIdList"]
        rankProb[i["rarityRank"]] = i["totalPercent"]
    if pool["detailInfo"]["weightUpCharInfoList"]:
        for i in pool["detailInfo"]["weightUpCharInfoList"]:
            rankChars[i["rarityRank"]] += [
                i["charId"]
                for j in range(
                    int(i["weight"]/100)-1
                )
            ]
    rankUpChars = {}
    rankUpProb = {}
    if pool["detailInfo"]["upCharInfo"]:
        for i in pool["detailInfo"]["upCharInfo"]["perCharList"]:
            rankUpChars[i["rarityRank"]] = i["charIdList"]
            rankUpProb[i["rarityRank"]] = i["percent"] * i["count"]
    pool_is_linkage = poolId.startswith("LINKAGE_")
    gachaTemp = read_json(GACHA_TEMP_JSON_PATH)
    if poolId not in gachaTemp:
        gachaTemp[poolId] = {
            "numWish": 0,
            "numWishUp": 0,
            "first5Star": 0
        }
    numWish = gachaTemp[poolId]["numWish"]
    numWishUp = gachaTemp[poolId]["numWishUp"]
    first5Star = gachaTemp[poolId]["first5Star"]
    for i in range(num):
        rankUpperLimit = {}
        if numWish < 50:
            rankUpperLimit[5] = rankProb[5]
        else:
            rankUpperLimit[5] = (numWish - 48)*rankProb[5]
        for j in range(4, 1, -1):
            rankUpperLimit[j] = rankUpperLimit[j+1]+rankProb[j]
        if pool_is_linkage and numWishUp == 119:
            rankUpperLimit[5] = 1
        if first5Star == 9:
            rankUpperLimit[4] = 1
        r = random.random()
        for rank in range(5, 1, -1):
            if r < rankUpperLimit[rank]:
                break
        if first5Star != -1:
            if rank >= 4:
                first5Star = -1
            else:
                first5Star += 1
        if rank == 5:
            numWish = 0
        else:
            numWish += 1
        if rank in rankUpChars:
            if (rank == 5 and numWishUp >= 150 and len(rankUpChars[rank]) == 1) or (pool_is_linkage and numWishUp == 119):
                r = 0
            else:
                r = random.random()
            if r < rankUpProb[rank]:
                char_id = random.choice(rankUpChars[rank])
                if numWishUp != -1:
                    if rank == 5:
                        numWishUp = -1
                    else:
                        numWishUp += 1
            else:
                char_id = random.choice(rankChars[rank])
                if numWishUp != -1:
                    numWishUp += 1
        else:
            char_id = random.choice(rankChars[rank])
            if numWishUp != -1:
                numWishUp += 1
        chars.append(
            {
                "charId": char_id,
                "isNew": 1
            }
        )
    gachaTemp[poolId]["numWish"] = numWish
    gachaTemp[poolId]["numWishUp"] = numWishUp
    gachaTemp[poolId]["first5Star"] = first5Star
    write_json(gachaTemp, GACHA_TEMP_JSON_PATH)
    return chars


def advancedGacha():
    request_json = request.json
    poolId = request_json["poolId"]
    config = read_json(CONFIG_PATH)
    simulateGacha = config["userConfig"]["simulateGacha"]
    if simulateGacha:
        chars = doWishes(1, poolId)
    else:
        gacha = read_json(GACHA_JSON_PATH)
        chars = gacha["advanced"]
    char_id = chars[0]["charId"]
    is_new = chars[0]["isNew"]
    char_inst_id = int(char_id.split('_')[1])
    return {
        "result": 0,
        "charGet": {
            "charInstId": char_inst_id,
            "charId": char_id,
            "isNew": is_new,
            "itemGet": [
                {
                    "type": "HGG_SHD",
                    "id": "4004",
                    "count": 999

                },
                {
                    "type": "LGG_SHD",
                    "id": "4005",
                    "count": 999
                },
                {
                    "type": "MATERIAL",
                    "id": f"p_{char_id}",
                    "count": 999
                }
            ],
            "logInfo": {}
        },
        "playerDataDelta": {
            "modified": {},
            "deleted": {}
        }
    }


def tenAdvancedGacha():
    request_json = request.json
    poolId = request_json["poolId"]
    config = read_json(CONFIG_PATH)
    simulateGacha = config["userConfig"]["simulateGacha"]
    if simulateGacha:
        chars = doWishes(10, poolId)
    else:
        gacha = read_json(GACHA_JSON_PATH)
        chars = gacha["advanced"]
    gachaResultList = []
    j = 0
    for i in range(10):
        char_id = chars[j]["charId"]
        is_new = chars[j]["isNew"]
        char_inst_id = int(char_id.split('_')[1])
        gachaResultList.append(
            {
                "charInstId": char_inst_id,
                "charId": char_id,
                "isNew": is_new,
                "itemGet": [
                    {
                        "type": "HGG_SHD",
                        "id": "4004",
                        "count": 999

                    },
                    {
                        "type": "LGG_SHD",
                        "id": "4005",
                        "count": 999
                    },
                    {
                        "type": "MATERIAL",
                        "id": f"p_{char_id}",
                        "count": 999
                    }
                ],
                "logInfo": {}
            }
        )
        j = (j+1) % len(chars)
    return {
        "result": 0,
        "gachaResultList": gachaResultList,
        "playerDataDelta": {
            "modified": {},
            "deleted": {}
        }
    }


def getPoolDetail():
    request_json = request.json
    poolId = request_json["poolId"]
    pool = doGetPool(poolId)
    return pool
