#!/bin/env python

import settings
from pymclevel import MCInfdevOldLevel
from pymclevel import TileEntity
from pymclevel import TAG_Compound
from pymclevel import TAG_List
from pymclevel import TAG_Short
from pymclevel import TAG_Byte
from pymclevel import TAG_String


def main():
    # Set random_seed explicitly just to avoid randomness
    level = MCInfdevOldLevel(settings.output_filename, create=True, random_seed=1)

    # Place the player
    px, py, pz = (2, 64, 2)
    level.setPlayerPosition( (px, py + 2, pz) )
    level.setPlayerSpawnPosition( (px, py, pz) )
    #print(dir(level.materials))
    #print(dir(level))

    create_empty_chunks(level, radius=12)

    dirt_island(level)
    sand_island(level)
    soul_sand_island(level)
    bedrock_island(level)
    obsidian_island(level)
    portal_island(level)

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
    chunk.Data[x, z, y] = 4  # facing west
    chest = TileEntity.Create('Chest')
    TileEntity.setpos(chest, (x, z, y))
    for item in contents:
        chest['Items'].append(item_stack(item))
    print(chest['Items'])
    # TODO: The following line crashes the client.  Find out why!
    # It appears to be triggered by the one in the bedrock island.
    # Possibility: the TileEntity is falling out of the world?
    chunk.TileEntities.append(chest)

def create_empty_chunks(level, radius = 0):
    for chunkX in range(-radius, radius + 1):
        for chunkZ in range(-radius, radius + 1):
            level.createChunk(chunkX, chunkZ)
            chunk = level.getChunk(chunkX, chunkZ)
            chunk.Blocks[:, :, :] = level.materials.Air.ID
            chunk.chunkChanged()

def dirt_island(level):
    # Main
    chunk = level.getChunk(0, 0)

    # Dirt
    dirt_id = level.materials.Dirt.ID
    chunk.Blocks[0:4, 0:4, 60:64] = dirt_id
    chunk.Blocks[4:8, 0:4, 60:64] = dirt_id
    chunk.Blocks[0:4, 4:8, 60:64] = dirt_id

    # Grass
    grass_id = level.materials.Grass.ID
    dirt = chunk.Blocks[:, :, 63] == dirt_id
    chunk.Blocks[:, :, 63][dirt] = grass_id
    chunk.chunkChanged()

    # Chest
    contents = [
            {'id': level.materials.Ice.ID,
                'count': 1, 'damage': 0, 'slot': 0},
            #{'id': level.materials.LavaBucket.ID,
                #'count': 1, 'damage': 0, 'slot': 0},
            ]
    make_chest(level, chunk, (7, 1, 64), contents)

def sand_island(level):
    # Main
    chunk = level.getChunk(-4, 0)

    # Sand
    sand_id = level.materials.Sand.ID
    chunk.Blocks[0:4, 0:4, 60:64] = sand_id

    # Cactus
    cactus_id = level.materials.Cactus.ID
    chunk.Blocks[0, 3, 64] = cactus_id

    # Chest
    contents = []
    make_chest(level, chunk, (2, 2, 64), contents)

    chunk.chunkChanged()

def soul_sand_island(level):
    # Nether
    pass

def bedrock_island(level):
    # Main
    chunk = level.getChunk(7, 2)

    # Bedrock
    bedrock_id = level.materials.Bedrock.ID
    chunk.Blocks[0:8, 0:8, 0:8] = bedrock_id

    # Air core
    air_id = level.materials.Air.ID
    chunk.Blocks[1:7, 1:7, 1:7] = air_id
    chunk.Blocks[:, :, 5] = air_id

    # End portal frame
    frame_id = level.materials.PortalFrame.ID
    chunk.Blocks[1:6, 2:5, 1] = frame_id
    chunk.Blocks[2:5, 1:6, 1] = frame_id
    chunk.Blocks[2:5, 2:5, 1] = air_id

    # Chest
    contents = []
    #make_chest(level, chunk, (3, 3, 1), contents)

    chunk.chunkChanged()

def obsidian_island(level):
    # End
    pass

def portal_island(level):
    # End
    pass

if __name__ == '__main__':
    main()
