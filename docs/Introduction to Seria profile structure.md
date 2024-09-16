# Introduction to Seria profile

[中文](Introduction%20to%20Seria%20profile%20structure.zh-cn.md)  

The Seria file is similar to the INI file for its key-value pair format and the JSON file for its curly bracket pairs. This makes it a hierarchical structure.  
Some key points we can observe from the file:

- The file can have nested bracket pairs inside another bracket pair
- The content inside a bracket pair always starts with the `m_classname` attribute.

With this in mind, we can start analysing the composition of the profile and understand the purpose of each part of the profile.  
Some terminology notice: because the Seria file has a tree-like structure, I will refer to each section as a node for convenience. For example, `Profile` is the root node and `Escadra` is a direct child node of the `Profile` node. However, it is also worth noticing that the Seria file has a `m_classname` named exactly `Node`. Care needs to be taken to distinguish between the meanings of the two.

## Profile composition

```
Profile
├── Escadra
|   [...]
├── Escadra
├── Location
|   [...]
├── Location
├── NPC
|   [...]
├── NPC
├── Item
|   [...]
├── Item
├── Node
└── LastPlayerPosData
```

Above is a typical profile structure in the middle of the campaign. `[...]` denotes a series of the same node as the previous one, they are being omitted here because there are dozens, hundreds of them.  
`Escadra`, as the name suggests, contains information about the ships on the map. This includes transport, strike group and player's fleet.  
`Location` contains information about the city on the map, this includes callsign, city type (e.g. Fuel Depot), parts and ammunition sold by the city.  
`NPC` contains information about all hireable characters in the game. Besides, all purchasable ships in a city are technically owned by an NPC (so they also have their own `NPC` node and if you take a close look, each NPC even has its own name and characteristic such as force and kindness).  
There are a few `Item` nodes that are directly stored as a child node of the root profile node. From what we know so far, these nodes contain information about the player's ammunition depot (because all ships can access it whether they are in a detachment or not, this is less related to a specific location or an escadra, I figure that's why it stores at the bottom of the profile).  
The last `Node` node (yes, its just named `Node`). Contains information about the paint mark (e.g. pencil marker and ruler) the player put on the map. Sometimes it's also being used to store inventory parts (I am not too sure about this, because the position where inventory parts can change between city or in-air fleet, need further verification)

### Escadra

```
Escadra
├── Node
│   ├── Frame
│   ├── Body
|   |   [...]
│   ├── Body
│   ├── Joint
│   |   [...]
│   └── Joint
├── Intel
|   [...]
├── Intel
├── Escadra::MapShip
└── Node
    ├── Body
    |   [...]
    └── Body
```

Above is a more detailed look at the `Escadra` node. The first node details the design of the ship. There are also intels that relate to the ship if it is an enemy ship or intercepted by a player ship. `Escadra::MapShip` is a node that details the ship's position on the strategic map. The last `Node` node within an `Escadra` node stores the information about the inventory parts of the fleet. Because we know that when a detachment acquires a part, that part will stay with the detachment before it is returned to the flagship. As a result, the parts are technically stored in individual ships. There are several `Body` nodes that lie within the `Node` node. Each `Body` node defines a type of part stored in that fleet (e.g. missile), its quantity and which ship's inventory it belongs to (this is crucial for inventory modification).  
Based on this information, it is technically possible for us to add or delete parts from a ship's inventory. Allowing real parts allocation possible, so that a detachment can get some missile supply from the flagship or simply cheat for any number of parts you want.

### Location

```
Location
├── Item
|   [...]
├── Item
└── Node
    ├── Body
    |   [...]
    └── Body
```

Above is a typical composition of a `Location` node. The first series of `Item` node contains information about ammunition sold in the supplies. Each `Item` node represent a type of ammunition. The last `Node` node contains information about each parts sold in the shipyard. Each `Body` node within the `Node` node represent a type of parts. This is similar to the ship's inventory.

## How to modify player's ammunition depot

```
m_items=2199023255555
{
m_classname=Item
m_code=2199023255555
m_index=31              <- type of ammunition
m_count=10              <- quantity of ammunition
}
```

Since we know that the last series of `Item` nodes is about player's ammunition. The modification is easy: just scroll down to the end of the profile. Identify which type of ammunition you want to change. Refer to the example above, `m_index` defines the type of ammunition and `m_count` is the quantity of that ammunition.

## How to modify a ship's inventory

```
m_listMapShips=1099511627779
{
m_classname=Escadra::MapShip
m_code=1099511627779
pBody.id=-463428086934121687
pEscadra.id=5264246570316703104     <- points to m_id of Escadra node
pCreature.id=-1392318650740825770
prevCurs=0.000243006
}
m_inventory=7
{
m_classname=Node
m_code=7
m_id=-2128173247453172687
m_children=15
{
m_classname=Body
m_code=15
m_id=3524251657124933523
m_name=BOMB
m_state=2
m_master_id=-2128173247453172687    <- points to m_id of Node (inventory) node
    [...]
{
m_classname=Mesh
m_size=4
    [...]
}
m_layer=3
m_slot_type=5
m_oid=MDL_BOMB_01                   <- type of this part
m_count=30                          <- quantiy of this part
is_loot=true
m_explosive=500
    [...]
}
    [...]
}
```

The easiest way to identify an `Node` (inventory) node is to look for the `Escadra::MapShip` node. Open a file editor and press the `ctrl`+`f` key to use the search function. The `Escadra::MapShip` node also contains useful attributes such as `pEscadra.id` to help you identify which ship this inventory belongs to. Since directly scrolling up is quite challenging. The outer `Node` node has a `m_id` attribute which is unique to each inventory. If you look at the `Body` node for the BOMB in this example, you will find out that there is a `m_master_id` that points to this inventory id.  
**When you copy/create parts to another inventory, you need to change these attributes accordingly to match the target inventory. Not doing so will cause the game to crash. So, be careful and remember to back up your file!**  
Another attribute that is worth noticing is the `m_count` attribute which defines the quantity of this part. And imagine having hundreds of missiles. We will bring peace to the Gerat (lol).

## Reference

[The Ultimate HighFleet Modding Guide](https://steamcommunity.com/sharedfiles/filedetails/?id=2768442721)
