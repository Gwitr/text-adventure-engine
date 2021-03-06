import json
import random
import datetime
import traceback

DEV_MODE = True

class Location():
    def __init__(self, connections=None, spawn_rate=0, text="", look="",
                 name="", items=None, unlocked=True, unlock_item=None,
                 enemy_classes=None):
        if not connections:
            self.connections = {"N": None, "S": None, "E": None, "W": None}
        else:
            self.connections = connections
        self.spawn_rate = spawn_rate
        self.text = text
        self.look = look
        self.name = name
        if items is None:
            self.items = {}
        else:
            self.items = items
        self.unlocked = unlocked
        self.unlock_item = unlock_item
        if enemy_classes is None:
            self.enemy_classes = []
        else:
            self.enemy_classes = enemy_classes

    def __repr__(self):
        return "Location(connections=%r, spawn_rate=%r, text=%r, look=%r, name=%r, items=%r, unlocked=%r, unlock_item=%r)\n" % (
            self.connections, self.spawn_rate, self.text, self.look, self.name, self.items, self.unlocked, self.unlock_item
        )

class Player():

    def __init__(self):
        self.hp = 100
        self.lvl = 1

class Enemy():
    
    def __init__(self, name, hp, strength, magic, move_chance):
        self.name = name
        self.hp = hp
        self.strength = strength
        self.magic = magic
        self.move_chance = move_chance

    def clone(self):
        return Enemy(self.name, self.hp, self.strength, self.magic,
                     self.move_chance)

def parse_text(text, locations, location):
    res = ""
    x = ""
    obj = ""
    field = ""
    val = ""
    neg = False
    mode = "normal"
    for i in text:
        if mode == "normal":
            if i == "%":
                mode = "possible_negation"
            else:
                res += i
        elif mode == "possible_negation":
            mode = "condition_obj"
            x = ""
            if i == "!":
                neg = True
            else:
                x += i
        elif mode == "condition_obj":
            if i == ":":
                obj = x
                x = ""
                mode = "condition_field"
            else:
                x += i
        elif mode == "condition_field":
            if i == "{":
                mode = "condition_text"
                field = x
                x = ""
            elif i == ":":
                mode = "condition_val"
                field = x
                x = ""
            else:
                x += i
        elif mode == "condition_val":
            if i == "{":
                mode = "condition_text"
                val = x
                x = ""
            else:
                x += i
        elif mode == "condition_text":
            if i == "}":
                b = locations[location].items[obj].compare(field, val)
                if neg:
                    b = not b
                if b:
                    res += x
                x = ""
                mode = "normal"
            else:
                x += i

    return res

def edit(locations, location):
    if not DEV_MODE:
        raise Exception("edit() invoked with DEV_MODE set to false!")
    if location != None:
        x = locations[location]
        print("Name:", x.name)
        print("Items:")
        for i in x.items:
            print("Item name:", i)
            print("Text:", x.items[i].itext)
            print("Text after collection:", x.items[i].itextcollected)
            print("Item type inside:", x.items[i].icontent)
            print("Item count inside:", x.items[i].icontentn)
        print("Connections:", x.connections)
        print("Text:", x.text)
        print("Look: ", x.look)
        print("Spawn rate (%): ", x.spawn_rate)
    name = input("Name: ")
    for i in range(len(locations)):
        if locations[i] is None:
            print("%4d:" % i, "NULL")
        else:
            print("%4d:" % i, locations[i].name)
    north = input("N Connection: ")
    south = input("S Connection: ")
    east  = input("E Connection: ")
    west  = input("W Connection: ")
    if north: north=int(north)
    else:     north=None
    if east:  east=int(east)
    else:     east=None
    if south: south=int(south)
    else:     south=None
    if west:  west=int(west)
    else:     west=None
    desc  = input("Text: ")
    print("> look")
    look  = input("Result: ")
    spawn = int(input("Spawn rate (%): "))

    unlock_item = input("Unlock item: ")
    if unlock_item == "":
        unlock_item = None
        unlocked = True
    else:
        unlocked = False

    items = {}
    while 1:
        iname = input("Item name: ")
        if iname == "":
            break
        itext = input("Inspection text: ")
        itextcollected = input("Inspection text after collection: ")
        icontent = input("Item type inside: ")
        icontentn = int(input("Item count inside: "))
        items[iname] = Inspectable(itext, itextcollected, icontent, icontentn)

    for i in range(len(enemy_classes)):
        print("%4d:" % i, enemy_classes[i].name)
    enemies = [int(i) for i in input("Enemy IDs: ").split(" ")]

    loc = Location()
    loc.name = name
    loc.items = items
    loc.connections = {"N": north, "S": south, "E": east, "W": west}
    loc.text = desc
    loc.look = look
    loc.spawn_rate = spawn
    loc.unlocked = unlocked
    loc.unlock_item = unlock_item
    loc.enemy_classes = enemies
    return loc

class Inspectable():
    def __init__(self, itext, itextcollected, icontent, icontentn):
        self.itext = itext
        self.icontent = icontent
        self.itextcollected = itextcollected
        self.collected = False
        self.icontentn = icontentn

    def compare(self, field, val=""):
        if field == "collected":
            return self.collected
        else:
            raise Exception("Unknown field %r" % field)

    def __repr__(self):
        return "Inspectable(%r, %r, %r, %r)" % (self.itext, self.itextcollected, self.icontent, self.icontentn)

class Item():
    def __init__(self, desc, cost, weapon, magic, magic_type):
        self.desc = desc
        self.cost = cost
        self.weapon = weapon
        self.magic  = magic
        self.magic_type = magic_type

    def __repr__(self):
        return "Item(%r, %r, %r, %r)" % (self.desc, self.cost, self.weapon,
                                         self.magic, self.magic_type)

def edit_item(item=None):
    if DEV_MODE:
        if item:
            print(item_classes[item])
        desc = input("Description: ")
        cost = int(input("Cost: "))
        weapon = int(input("Strength: "))
        magic = int(input("Magic strength: "))
        magic_type = input("Magic type: ")

        return Item(desc, cost, weapon, magic, magic_type)
    else:
        raise Exception("edit_item() invoked with DEV_MODE set to false!")

class MySerializer(json.JSONEncoder):
    def default(self, obj):
        if type(obj) == Location:
            return {"connections": obj.connections, "spawn_rate": obj.spawn_rate,
                    "text": obj.text, "look": obj.look, "name": obj.name,
                    "inspectables": {item: self.default(obj.items[item]) for item in obj.items},
                    "unlocked": obj.unlocked, "unlock_item": obj.unlock_item,
                    "enemy_classes": obj.enemy_classes}
        elif type(obj) == Inspectable:
            return {"text": obj.itext, "text_collected": obj.itextcollected,
                    "content": obj.icontent, "contentn": obj.icontentn}
        elif type(obj) == Item:
            return [obj.desc, obj.cost, obj.weapon, obj.magic,
                    obj.magic_type]
        elif type(obj) == Enemy:
            return [obj.name, obj.hp, obj.strength,
                    obj.magic, obj.move_chance]
        else:
            return obj

def edit_enemy():
    name = input("Name: ")
    hp   = int(input("HP: "))
    sght = int(input("Strength: "))
    mgic = int(input("Magic: "))
    mvch = int(input("Move chance: "))

    return Enemy(name, hp, sght, mgic, mvch)

def enemy_fight(player, inv, enemy):
    enemy = enemy.clone()
    print("A %s attacked!" % (enemy.name))
    strength = 0
    while 1:
        while 1:
            x = input("> ")
            cmd, *args = x.split(" ")
            if cmd == "inventory":
                for i in inv:
                    print(i, inv[i], "(strength:", item_classes[i].weapon, ")")
                

            elif cmd == "attack":
                attack = random.randint(80, 120) / 100 * strength
                print("Dealt %d damage!" % attack)
                enemy.hp -= attack
                if enemy.hp < 0:
                    enemy.hp = 0
                print("The enemy has %d HP left." % (enemy.hp))
                break
            elif cmd == "equip":
                if len(args) == 0:
                    print("Equip what?")
                else:
                    if args[0] not in item_classes:
                        print("Can't equip", args[0])
                    elif args[0] not in inv:
                        print("Can't equip", args[0])
                    elif item_classes[args[0]].weapon == 0:
                        print("Can't equip", args[0])
                    else:
                        strength = item_classes[args[0]].weapon * ((player.lvl+10)/10)
                break

        print("The enemy attacked!")
        attack = random.randint(80, 120) / 100 * enemy.strength
        player.hp -= attack
        print("You have %d HP left" % player.hp)

        if enemy.hp < 1:
            print("You win!")
            prev = player.lvl
            player.lvl += 0.4
            if int(prev) != player.lvl:
                print("Got a new level!")
            break

# The worst code I ever wrote
try:
    with open("game.json") as f:
        j = json.load(f)
    item_classes = {i: Item(
        j["item_classes"][i][0],
        j["item_classes"][i][1],
        j["item_classes"][i][2],
        j["item_classes"][i][3],
        j["item_classes"][i][4],
    ) for i in j["item_classes"]}
    locations = []
    for i in j["locations"]:
        items = {}
        for ii in i["inspectables"]:
            items[ii] = Inspectable(i["inspectables"][ii]["text"], i["inspectables"][ii]["text_collected"],
                                     i["inspectables"][ii]["content"], i["inspectables"][ii]["contentn"])
        locations.append(Location(i["connections"], i["spawn_rate"], i["text"],
                                  i["look"], i["name"], items, False if i["unlock_item"] else True,
                                  i["unlock_item"], i["enemy_classes"]))
    enemy_classes = []
    for i in j["enemy_classes"]:
        enemy_classes.append(Enemy(*i))
except FileNotFoundError:
    print("Couldn't load game.json, forcing dev mode")
    DEV_MODE = True
    item_classes = {}
    locations = []
    enemy_classes = []
except:
    if not DEV_MODE:
        raise
    print("Couldn't load map:")
    traceback.print_exc()
    item_classes = {}
    locations = []

dirmap = {
                    "north": "N",
                    "east": "E",
                    "south": "S",
                    "west": "W",
                    "n": "N",
                    "s": "S",
                    "e": "E",
                    "w": "W",
                }
location = 0
inv = {}
player = Player()
while 1:
    if location >= len(locations):
        pass
    elif locations[location] is None:
        pass
    else:
        print(parse_text(locations[location].text, locations, location))
        if random.randint(0, 100) >= (100 - locations[location].spawn_rate):
            if len(locations[location].enemy_classes) > 0:
                enemyid = random.choice(locations[location].enemy_classes)
                if enemyid < len(enemy_classes):
                    enemy_fight(player, inv, enemy_classes[enemyid])
                else:
                    print("Enemy %d not found" % enemyid)
                    enemy_classes.append(edit_enemy())
        while 1:
            x = input("> ")
            cmd, *args = x.split(" ")
            if cmd == "look":
                print(parse_text(locations[location].look, locations, location))
            elif cmd == "go":
                if len(args) == 0:
                    print("To where?")
                else:
                    to = locations[location].connections[dirmap[args[0]]]
                    if to is None:
                        print("Can't go", args[0])
                    elif to >= len(locations):
                        location = to
                        break
                    elif locations[to].unlocked:
                        location = to
                        break
                    else:
                        print("Can't go", args[0])
            elif cmd == "edit":
                if DEV_MODE:
                    if len(args) == 2:
                        if args[0] == "item":
                            item_classes[args[1]] = edit_item(args[1])
                        else:
                            print("I don't understand.")
                    locations[location] = edit(locations, location)
            elif cmd == "inspect":
                if len(args) == 0:
                    print("Inspect what?")
                else:
                    args = [" ".join(args), ]
                    if args[0] not in locations[location].items:
                        print("Can't inspect", args[0])
                    else:
                        if locations[location].items[args[0]].collected:
                            print(locations[location].items[args[0]].itextcollected)
                        else:
                            print(locations[location].items[args[0]].itext)
            elif cmd == "collect":
                if len(args) == 0:
                    print("Collect what?")
                else:
                    args = [" ".join(args), ]
                    if args[0] not in locations[location].items:
                        print("Can't collect", args[0])
                    elif locations[location].items[args[0]].icontentn == 0:
                        print("Can't collect", args[0])
                    else:
                        if locations[location].items[args[0]].icontent not in item_classes:
                            print("Item %s doesn't exist" % (locations[location].items[args[0]].icontent))
                            item_classes[locations[location].items[args[0]].icontent] = edit_item()
                        elif locations[location].items[args[0]].collected:
                            print("Can't collect", args[0])
                        else:
                            print("Added %d %s to your inventory!" % (locations[location].items[args[0]].icontentn, locations[location].items[args[0]].icontent))
                            if locations[location].items[args[0]].icontent not in inv:
                                inv[locations[location].items[args[0]].icontent] = 0
                            inv[locations[location].items[args[0]].icontent] += locations[location].items[args[0]].icontentn
                            locations[location].items[args[0]].collected = True
            elif cmd == "help":
                print("quit - quit")
                print("look - looks around")
                print("inspect <object> - inspects object")
                print("go <direction> - goes to direction")
                print("collect <object> - collects object / whatever is inside object")
                print("use <item> <direction> - Uses an item on a direction.")
                if DEV_MODE:
                    print("edit - edits current room")
                    print("edit item <item name> - edits item class")
                    print("save_dev - saves the new game version")
            
            elif cmd == "save_dev":
                if DEV_MODE:
                    x = datetime.datetime.now()
                    try:
                        with open("game.json", "r") as fr:
                            with open("game_backup%s.json" % (x.strftime("%d_%m_%Y_%H_%M")), "w") as fw:
                                fw.write(fr.read())
                    except FileNotFoundError:
                        print("Couldn't back up game.json: File not found")
                    
                    j = json.dumps({
                        "item_classes": item_classes,
                        "locations": locations,
                        "enemy_classes": enemy_classes
                    }, cls=MySerializer, indent=4)
                    with open("game.json", "w") as f:
                        f.write(j)
            
            elif cmd == "use":
                if len(args) == 0:
                    print("What?")
                elif len(args) == 1:
                    print("Where? (n/s/e/w)")
                else:
                    if args[0] not in inv:
                        print("I don't have an item called %r." % (args[0]))
                    elif inv[args[0]] == 0:
                        print("I don't have any %s's left." % (args[0]))
                    else:
                        dir = dirmap[args[1]]
                        if locations[location].connections[dir] == None:
                            print("Nothing to use this item on!")
                        else:
                            inv[args[0]] -= 1
                            other_location = locations[locations[location].connections[dir]]
                            if other_location.unlocked:
                                print("Nothing happened...")
                            elif other_location.unlock_item == args[0]:
                                print("Used %s!" % (args[0]))
                                other_location.unlocked = True
                            else:
                                print("Nothing happened...")

            elif cmd == "quit":
                raise SystemExit(0)
        continue
    print("Map %d doesn't exist. Map creation mode: " % (location))
    locations.append(edit(locations, None))
