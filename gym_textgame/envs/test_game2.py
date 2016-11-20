#!/usr/bin/python
#
# author:
#
# date:
# description:
#
from textgame_env2 import HomeWorld2

def moveBlocked(env, room, direction):
    env.state["room"] = room
    env.do("go " + direction)
    assert env.state["room"] == room, "Room {} is not blocked in direction {}".format(room,direction)

def changeRoom(env, room1, direction, room2):
    env.state["room"] = room1
    env.do("go " + direction)
    assert env.state["room"] == room2, ("Wrong room transition {} to {} with direction {}".format(room1,room2,direction))

blockedTest = [
    ("hall","west"),("hall","north"),("hall","south"),
    ("living","north"),
    ("garden","north"),("garden","east"),
    ("bedroom","south"),("bedroom","west"),
    ("kitchen","east"),
    ("pantry","south"),("pantry","west"),("pantry","east"),]

moveTest = [
    ("hall","east","living"),
    ("living","south","bedroom"),("living","east","garden"),("living","west","hall"),
    ("garden","south","kitchen"),("garden","west","living"),
    ("bedroom","north","living"),("bedroom","east","kitchen"),
    ("kitchen","south","pantry"),("kitchen","west","bedroom"),
    ("pantry","north","kitchen"),
]

questCompleteTest = [
    ()
]

env = HomeWorld2()

for r,d in blockedTest:
    env.reset()
    moveBlocked(env,r,d)
print "passed blockedTest"
for r1,d,r2 in moveTest:
    env.reset()
    changeRoom(env,r1,d,r2)
print "passed changing room test"

env.reset()
env.state["quest"] = "bored"
env.state["room"] = "living"
env.state["energy"] = False
env.do("watch tv")
assert env.state["quest"] == "bored"
assert env.state["info"] == "energy_error"

env.reset()
env.state["quest"] = "bored"
env.state["room"] = "living"
env.state["energy"] = True
env.do("watch tv")
assert env.state["quest"] == ""
assert env.state["info"] == ""

env.reset()
env.state["quest"] = "hungry"
env.state["room"] = "kitchen"
env.state["poisoned"] = "apple"
env.do("eat apple")
assert env.state["quest"] == "hungry"
assert env.state["dead"] == True

env.reset()
env.state["quest"] = "hungry"
env.state["room"] = "kitchen"
env.state["poisoned"] = "pizza"
env.state["old"] = "apple"
env.do("eat apple")
assert env.state["quest"] == "hungry"
assert env.state["info"] == "old_food"
assert env.state["dead"] == False

env.reset()
env.state["quest"] = "hungry"
env.state["room"] = "kitchen"
env.state["poisoned"] = "cheese"
env.state["old"] = "pizza"
env.do("eat apple")
assert env.state["quest"] == ""
assert env.state["dead"] == False
