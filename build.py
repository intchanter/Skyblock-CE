#!/bin/env python

import settings
from pymclevel import MCInfdevOldLevel
from pymclevel import TileEntity
from pymclevel import TAG_Compound
from pymclevel import TAG_List
from pymclevel import TAG_Short
from pymclevel import TAG_Byte
from pymclevel import TAG_String
#from pymclevel.items.items import 

# So we can use relative figures and shift them all around slightly
base = 4


def main():
    # Set random_seed explicitly just to avoid randomness
    level = MCInfdevOldLevel(settings.output_filename, create=True, random_seed=1)
    #level = MCInfdevOldLevel(settings.output_filename)

    # Place the player
    px, py, pz = (6, 64, 6)
    level.setPlayerPosition( (px, py + 2, pz) )
    level.setPlayerSpawnPosition( (px, py, pz) )
    #print(dir(level.materials))
    #print(dir(level))

    create_empty_chunks(level, radius=15)
    #empty_precreated_chunks(level, radius=15)

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
    chunk.Blocks[x, z, y] = chest_id
    chest_facing_west = 4
    chunk.Data[x, z, y] = chest_facing_west
    #chest = TileEntity.Create('Chest')
    #TileEntity.setpos(chest, (x, z, y))
    #for item in contents:
    #    chest['Items'].append(item_stack(item))
    #print(chest['Items'])
    # TODO: The following line crashes the client.  Find out why!
    # It appears to be triggered by the one in the bedrock island.
    # Possibility: the TileEntity is falling out of the world?
    # No, they don't seem able to do that.
    # Okay, even without creating the chest in the bedrock island,
    # I get the crash when moving to a different chunk.  Maybe
    # it's something to do with biomes and the way I'm clearing
    # chunks?
    # Expanding the generated world out further avoids it for now.
    # Unless I add block entities or other entities manually.
    # The error message seems to refer to there being a negative
    # distance to some entity.  How is that even possible?
    #chunk.TileEntities.append(chest)

def create_empty_chunks(level, radius=0):
    for chunkX in range(-radius, radius + 1):
        for chunkZ in range(-radius, radius + 1):
            level.createChunk(chunkX, chunkZ)
            chunk = level.getChunk(chunkX, chunkZ)
            chunk.chunkChanged()

def empty_precreated_chunks(level, radius=0):
    for chunkX, chunkZ in level.allChunks:
        chunk = level.getChunk(chunkX, chunkZ)
        print(chunk.Entities)
        print(chunk.TileEntities)
        chunk.Blocks[:, :, :] = level.materials.Air.ID
        chunk.Data[:, :, :] = 0
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
            #{'id': level.materials.Ice.ID,
            {'id': 79,
                'count': 1, 'damage': 0, 'slot': 0},
            #{'id': level.materials.LavaBucket.ID,
                #'count': 1, 'damage': 0, 'slot': 0},
            ]
    make_chest(level, chunk, (base+7, base+2, 64), contents)

def sand_island(level, chunkX, chunkY):
    # Main
    chunk = level.getChunk(chunkX, chunkY)

    # Sand
    sand_id = level.materials.Sand.ID
    chunk.Blocks[base:base+4, base:base+4, 60:64] = sand_id

    # Cactus
    cactus_id = level.materials.Cactus.ID
    chunk.Blocks[base, base+3, 64] = cactus_id

    # Chest
    contents = []
    make_chest(level, chunk, (base+2, base+2, 64), contents)

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
    contents = []
    make_chest(level, chunk, (base+2, base+2, 64), contents)

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
    chunk.Blocks[base:base+8, base:base+8, base:base+8] = bedrock_id

    # Air core
    air_id = level.materials.Air.ID
    chunk.Blocks[base+1:base+7, base+1:base+7, 1:7] = air_id
    chunk.Blocks[:, :, 5] = air_id

    # End portal frame
    frame_id = level.materials.PortalFrame.ID
    chunk.Blocks[base+1:base+6, base+2:base+5, 1] = frame_id
    chunk.Blocks[base+2:base+5, base+1:base+6, 1] = frame_id
    chunk.Blocks[base+2:base+5, base+2:base+5, 1] = air_id

    # Chest
    contents = []
    make_chest(level, chunk, (base+3, base+3, 1), contents)

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

    # Bedrock
    bedrock_id = level.materials.Bedrock.ID

    # Portal

    # Torches

    # Dragon Egg

    chunk.chunkChanged()

if __name__ == '__main__':
    main()
