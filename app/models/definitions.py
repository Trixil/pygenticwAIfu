from pydantic import BaseModel, Field
from typing import Any

def ensure_list(value: Any) -> list:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


class LLMConfig(BaseModel):
    LLMName: str = ""
    temp: float = 0.0
    maxTokens: int = 0
    topP: float = 1

class character(BaseModel):
    charName: str = ""
    charNickname: str = ""
    charDesc: str = ""
    charScenario: str = ""
    charExampleDialogue: str = ""
    charFile: str = ""
    charImageFile: str = ""

class agent(BaseModel):
    agentName: str = ""
    agentInstructions: str = ""
    agentLLMConfig: LLMConfig = Field(default_factory=LLMConfig)

class agentPipeline(BaseModel):
    agentSequence: dict[int, agent] = Field(default_factory=dict)
    outputFlow: dict[str, list[str]] = Field(default_factory=dict)
    pastMessageCount: dict[str, int] = Field(default_factory=dict)
    includeCharCards: dict[str, bool] = Field(default_factory=dict)

class agentLoadout(BaseModel):
    loadoutName: str = ""
    loadoutImageFile: str = ""
    loadoutFile: str = ""
    loadoutAgents: dict[str, agent] = Field(default_factory=dict)
    loadoutPipeline: agentPipeline = Field(default_factory=agentPipeline)

class message(BaseModel):
    role: str = ""
    sender: str = ""
    content: str  = ""

class chat(BaseModel):
    chatName: str = ""
    chatID: int = 0
    chatFile: str = ""
    chatAgentLoadout: str = ""
    chatCharacters: list[str] = Field(default_factory=list)
    messages: list[message] = Field(default_factory=list)



    #cleanChat = grungyChat
    #
    #singleFields = ["chatName", "chatID", "chatFile"]
    #cleanChat = {}
    #cleanChat = {
    #    field: grungyChat.get(field)
    #    for field in singleFields
    #}
    #cleanChat["chatName"] = grungyChat["chatName"]
    #cleanChat["chatID"] = grungyChat["chatID"]
    #cleanChat["chatFile"] = grungyChat["chatFile"]
    #cleanChat["loadoutAgents"] = ensure_list(grungyChat["loadoutAgents"])
    #cleanChat["loadoutAgents"] = {\

#messy_chat_json = {
#    "chatName": "Test Chat",
#    "chatID": "42",
#    "chatFile": "test-chat.json",
#
#    # This is present, but nested fields are messy.
#    "chatAgentLoadout": {
#        "loadoutName": "Experimental Loadout",
#        "loadoutFile": "experimental-loadout.json",
#
#        # Should be dict[str, agent], but one agent has missing config fields.
#        "loadoutAgents": {
#            "planner": {
#                "agentName": "Planner",
#                "agentInstructions": "Decide what should happen next.",
#                "agentLLMConfig": {
#                    "LLMName": "gpt-test",
#                    "temp": "0.7",
#                    "maxTokens": "800"
#                    # topP missing
#                }
#            },
#            "writer": {
#                "agentName": "Writer"
#                # agentInstructions missing
#                # agentLLMConfig missing
#            }
#        },
#
#        "loadoutPipeline": {
#            # Should be dict[int, Agent], but JSON keys are strings.
#            "agentSequence": {
#                "1": {
#                    "agentName": "Planner",
#                    "agentInstructions": "Plan the next beat."
#                },
#                "2": {
#                    "agentName": "Writer",
#                    "agentInstructions": "Write the response."
#                }
#            },
#
#            # Should be dict[str, list[str]], but planner has a single string.
#            "outputFlow": {
#                "planner": "writer",
#                "writer": ["final"]
#            },
#
#            # Should be dict[str, int], but values are mixed.
#            "pastMessageCount": {
#                "planner": "8",
#                "writer": None,
#                "critic": "not-a-number"
#            },
#
#            # Should be dict[str, bool], but values are mixed.
#            "includeCharCards": {
#                "planner": "true",
#                "writer": "false",
#                "critic": 1,
#                "debugger": 0
#            }
#        }
#    },
#
#    # Should be list[character], but this is a single dict.
#    "chatCharacters": {
#        "charName": "Mira",
#        "charDesc": "A cautious engineer.",
#        "charScenario": "Trapped in a failing orbital station.",
#        "charFile": "mira.json"
#    },
#
#    # Should be list[message], but this is also a single dict.
#    "messages": {
#        "role": "user",
#        "sender": "Player",
#        "content": "Check the oxygen system."
#    }
#}
