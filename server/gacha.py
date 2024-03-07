from flask import request

from constants import GACHA_JSON_PATH
from utils import read_json, write_json, decrypt_battle_data
from core.function.update import updateData

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


def advancedGacha():
    request_json = request.json
    gacha = read_json(GACHA_JSON_PATH)
    char_id = gacha["advanced"][0]["charId"]
    char_inst_id = int(char_id.split('_')[1])
    is_new = gacha["advanced"][0]["isNew"]
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
    gacha = read_json(GACHA_JSON_PATH)
    chars = gacha["advanced"]
    gachaResultList = []
    j = 0
    for i in range(10):
        char_id = chars[j]["charId"]
        char_inst_id = int(char_id.split('_')[1])
        is_new = chars[j]["isNew"]
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
