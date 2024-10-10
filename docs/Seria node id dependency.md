# Seria node id dependency

When adding a new ship node from a design file to a player's profile, `m_id` must be handled carefully and made unique among all other `m_id`. This is because `m_id` is also referenced by other attributes such as `m_master_id` and `m_owner_id`. A ship design file, by default, contains existing ids. When adding multiple ship nodes to the profile, ids must be changed to avoid collision. Having duplicate id will cause the game to crash.

## Body

|Dependency|Consumer|
|-|-|
|m_id|[Creature](#creature) m_master_id|
||[Joint](#joint) m_A.id|
||[Joint](#joint) m_B.id|
||[Slot](#slot) m_master.id|
||[Slot](#slot) m_block.id|
|m_master_id||
|m_owner_id||

## Creature

|Dependency|Consumer|
|-|-|
|m_id|m_owner_id (self)|
||[Body](#body) m_owner_id|
||[Frame](#frame) m_owner_id|
|m_master_id||
|m_owner_id||

## Escadra

Root node of a fleet in profile.

m_id

## Frame

|Dependency|Consumer|
|-|-|
|m_id|[Body](#body) m_master_id|
|m_master_id||
|m_owner_id||

## Joint

|Dependency|Consumer|
|-|-|
|m_master.id||
|m_A.id||
|m_B.id||

## Node

Root node of a ship design.

|Dependency|Consumer|
|-|-|
|m_id|[Body](#body) m_master_id|
||[Frame](#frame) m_master_id|
||[Joint](#joint) m_master.id|
|m_master_id|[Escadra](#escadra) m_id|

## Slot

m_master.id  
m_block.id
