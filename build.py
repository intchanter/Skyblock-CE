#!/bin/env python

import settings
from pymclevel import MCInfdevOldLevel
from pymclevel import TileEntity
from pymclevel import TAG_Compound
from pymclevel import TAG_List
from pymclevel import TAG_Short
from pymclevel import TAG_Byte
from pymclevel import TAG_String
from pymclevel.items import items

# So we can use relative figures and shift them all around slightly
base = 4


def main():
    # Set random_seed explicitly just to avoid randomness
    level = MCInfdevOldLevel(settings.output_filename, create=True, random_seed=1)
    # TODO: The following line is for testing only.  Be sure it's
    # commented out before releasing!
    level.GameType = level.GAMETYPE_CREATIVE

    # Place the player
    px, py, pz = (6, 64, 6)
    level.setPlayerPosition( (px, py + 2, pz) )
    level.setPlayerSpawnPosition( (px, py, pz) )

    create_empty_chunks(level, radius=15)

    # overworld
    dirt_island(level, 0, 0)
    sand_island(level, -1, 0)
    bedrock_island(level, 1, 0)

    # nether
    soul_sand_island(level, 0, -1)

    # end
    obsidian_island(level, 0, 1)
    portal_island(level, -1, 1)

    level.generateLights()
    level.saveInPlace()

def item_stack(item):
    item_tag = TAG_Compound()
    item_tag.name = ''
    item_tag['id'] = TAG_Short(item['id'])
    item_tag['Damage'] = TAG_Short(item['damage'])
    item_tag['Count'] = TAG_Byte(item['count'])
    item_tag['Slot'] = TAG_Byte(item['slot'])
    return item_tag

def make_chest(level, chunk, pos, contents):
    x, z, y = pos
    chest_id = level.materials.Chest.ID
    chunk.Blocks[x % 16, z % 16, y] = chest_id
    chest_facing_west = 4
    chunk.Data[x % 16, z % 16, y] = chest_facing_west
    chest = TileEntity.Create('Chest')
    TileEntity.setpos(chest, (x, y, z))
    slot = 0
    for item in contents:
        item['slot'] = slot
        chest['Items'].append(item_stack(item))
        slot += 1
    chunk.TileEntities.append(chest)

def create_empty_chunks(level, radius=0):
    dimensions = [level.getDimension(-1), level, level.getDimension(1)]
    for dimension in dimensions:
        for chunkX in range(-radius, radius + 1):
            for chunkZ in range(-radius, radius + 1):
                dimension.createChunk(chunkX, chunkZ)
                chunk = dimension.getChunk(chunkX, chunkZ)
                chunk.chunkChanged()

def dirt_island(level, chunkX, chunkZ):
    # Main
    chunk = level.getChunk(chunkX, chunkZ)

    # Dirt
    dirt_id = level.materials.Dirt.ID
    chunk.Blocks[base:base+8, base:base+4, 60:64] = dirt_id
    chunk.Blocks[base:base+4, base+4:base+8, 60:64] = dirt_id

    # Grass
    grass_id = level.materials.Grass.ID
    dirt = chunk.Blocks[:, :, 63] == dirt_id
    chunk.Blocks[:, :, 63][dirt] = grass_id
    chunk.chunkChanged()

    # Tree
    log_id = level.materials.Wood.ID
    leaf_id = level.materials.Leaves.ID
    chunk.Blocks[base-1:base+2, base+5:base+10, 67:69] = leaf_id
    chunk.Blocks[base-2:base+3, base+6:base+9, 67:69] = leaf_id
    chunk.Blocks[base, base+6:base+9, 69:71] = leaf_id
    chunk.Blocks[base-1:base+2, base+7, 69:71] = leaf_id
    chunk.Blocks[base-2, base+5, 67] = leaf_id
    chunk.Blocks[base-2, base+9, 68] = leaf_id
    chunk.Blocks[base-1:base+2, base+6:base+9, 69] = leaf_id
    chunk.Blocks[base, base+7, 64:70] = log_id

    # Chest
    contents = [
            {'id': items.names['Ice'],
                'count': 1, 'damage': 0},
            {'id': items.names['Lava Bucket'],
                'count': 1, 'damage': 0},
            ]
    chunkX *= 16
    chunkZ *= 16
    make_chest(level, chunk, (chunkX+base+7, chunkZ+base+2, 64), contents)

def sand_island(level, chunkX, chunkZ):
    # Main
    chunk = level.getChunk(chunkX, chunkZ)

    # Sand
    sand_id = level.materials.Sand.ID
    chunk.Blocks[base:base+4, base:base+4, 60:64] = sand_id

    # Cactus
    cactus_id = level.materials.Cactus.ID
    chunk.Blocks[base, base+3, 64] = cactus_id

    # Chest
    contents = [
            {'id': items.names['Obsidian'],
                'count': 10, 'damage': 0},
            # The melon slice item can't be referenced due to a name conflict
            # TODO: I submitted a patch to pymclevel's items.py for this.
            # Once it goes in, use the following line instead.
            #{'id': items.names['Melon Slice'],
            {'id': items.names['Melon'],
                'count': 1, 'damage': 0},
            ]
    # Entities need the world-wide coordinates?!
    chunkX *= 16
    chunkZ *= 16
    make_chest(level, chunk, (chunkX+base+2, chunkZ+base+2, 64), contents)

    chunk.chunkChanged()

def soul_sand_island(level, chunkX, chunkZ):
    chunk = level.getChunk(chunkX, chunkZ)

    # Soul Sand
    soul_sand_id = level.materials.SoulSand.ID
    chunk.Blocks[base:base+4, base:base+4, 60:64] = soul_sand_id

    # Obsidian
    obsidian_id = level.materials.Obsidian.ID
    chunk.Blocks[base-1, base+1:base+3, 63] = obsidian_id
    chunk.Blocks[base-1, base+1:base+3, 67] = obsidian_id
    chunk.Blocks[base-1, base, 64:67] = obsidian_id
    chunk.Blocks[base-1, base+3, 64:67] = obsidian_id

    # Portal
    portal_id = level.materials.NetherPortal.ID
    chunk.Blocks[base-1, base+1:base+3, 64:67] = portal_id

    # Chest
    contents = [
            {'id': items.names['Ice'],
                'count': 1, 'damage': 0},
            ]
    chunkX *= 16
    chunkZ *= 16
    make_chest(level, chunk, (chunkX+base+2, chunkZ+base+2, 64), contents)

    # Mushrooms and Netherwart
    red_mushroom_id = level.materials.RedMushroom.ID
    brown_mushroom_id = level.materials.BrownMushroom.ID
    netherwart_id = level.materials.NetherWart.ID
    chunk.Blocks[base+3, base, 64] = red_mushroom_id
    chunk.Blocks[base, base+3, 64] = brown_mushroom_id
    chunk.Blocks[base, base, 64] = netherwart_id

    chunk.chunkChanged()

def bedrock_island(level, chunkX, chunkZ):
    chunk = level.getChunk(chunkX, chunkZ)

    # Bedrock
    bedrock_id = level.materials.Bedrock.ID
    chunk.Blocks[base:base+8, base:base+8, :8] = bedrock_id

    # Air core
    air_id = level.materials.Air.ID
    water_id = level.materials.Water.ID
    chunk.Blocks[base+1:base+7, base+1:base+7, 1:7] = air_id
    chunk.Blocks[:, :, 5] = air_id

    # End portal frame
    frame_id = level.materials.PortalFrame.ID
    chunk.Blocks[base+1:base+6, base+2:base+5, 1] = frame_id
    chunk.Blocks[base+2:base+5, base+1:base+6, 1] = frame_id
    chunk.Blocks[base+2:base+5, base+2:base+5, 1] = air_id
    chunk.Data[base+2:base+5, base+1, 1] = 0
    chunk.Data[base+5, base+2:base+5, 1] = 1
    chunk.Data[base+2:base+5, base+5, 1] = 2
    chunk.Data[base+1, base+2:base+5, 1] = 3

    # Chest
    contents = [
            {'id': items.names['Ice'],
                'count': 1, 'damage': 0},
            ]
    chunkX *= 16
    chunkZ *= 16
    make_chest(level, chunk, (chunkX+base+3, chunkZ+base+3, 1), contents)

    chunk.chunkChanged()

def obsidian_island(level, chunkX, chunkZ):
    # End
    chunk = level.getChunk(chunkX, chunkZ)

    # Obsidian
    obsidian_id = level.materials.Obsidian.ID
    chunk.Blocks[base:base+4, base:base+4, 60:64] = obsidian_id

    chunk.chunkChanged()

def portal_island(level, chunkX, chunkZ):
    # End
    chunk = level.getChunk(chunkX, chunkZ)

    # Bedrock frame
    bedrock_id = level.materials.Bedrock.ID
    chunk.Blocks[base-2:base+3, base-1:base+2, 63] = bedrock_id
    chunk.Blocks[base-1:base+2, base-2:base+3, 63] = bedrock_id
    chunk.Blocks[base-1:base+2, base-3:base+4, 64] = bedrock_id
    chunk.Blocks[base-2:base+3, base-2:base+3, 64] = bedrock_id
    chunk.Blocks[base-3:base+4, base-1:base+2, 64] = bedrock_id

    # Portal
    portal_id = level.materials.EnderPortal.ID
    chunk.Blocks[base-2:base+3, base-1:base+2, 64] = portal_id
    chunk.Blocks[base-1:base+2, base-2:base+3, 64] = portal_id

    # Bedrock spire
    chunk.Blocks[base, base, 63:68] = bedrock_id

    # Torches
    torch_id = level.materials.Torch.ID
    chunk.Blocks[base+0, base-1, 66], chunk.Data[base+0, base-1, 66] = (torch_id, 4)
    chunk.Blocks[base+1, base+0, 66], chunk.Data[base+1, base+0, 66] = (torch_id, 1)
    chunk.Blocks[base+0, base+1, 66], chunk.Data[base+0, base+1, 66] = (torch_id, 3)
    chunk.Blocks[base-1, base+0, 66], chunk.Data[base-1, base+0, 66] = (torch_id, 2)

    # Dragon Egg
    dragon_egg_id = level.materials.DragonEgg.ID
    chunk.Blocks[base, base, 68] = dragon_egg_id

    chunk.chunkChanged()

if __name__ == '__main__':
    main()
