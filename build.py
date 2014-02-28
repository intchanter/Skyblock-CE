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
    level = MCInfdevOldLevel(settings.output_filename, create=True)
    level.setPlayerPosition( (2, 67, 2) )
    level.setPlayerSpawnPosition( (2, 64, 2) )
    clear_chunks(level, radius = 12)
    dirt_island(level)
    sand_island(level)
    level.generateLights()
    level.saveInPlace()

def clear_chunks(level, radius = 0):
    for chunkX in range(-radius, radius + 1):
        for chunkZ in range(-radius, radius + 1):
            chunk = level.getChunk(chunkX, chunkZ)
            chunk.Blocks[:, :, :] = level.materials.Air.ID
            chunk.chunkChanged()

def dirt_island(level):
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
    chest_id = level.materials.Chest.ID
    chunk.Blocks[7, 1, 64] = chest_id
    chunk.Data[7, 1, 64] = 4
    chest_inventory = level.tileEntityAt(7, 1, 64)

    print(chest_inventory)
    print(dir(chest_inventory))


def sand_island(level):
    chunk = level.getChunk(-4, 0)

    # Sand
    sand_id = level.materials.Sand.ID
    chunk.Blocks[0:4, 0:4, 60:64] = sand_id

    # Cactus
    cactus_id = level.materials.Cactus.ID
    chunk.Blocks[0, 3, 64] = cactus_id

    # Chest
    chest_id = level.materials.Chest.ID
    chunk.Blocks[7, 1, 64] = chest_id
    chunk.Data[7, 1, 64] = 4
    chest_inventory = level.tileEntityAt(7, 1, 64)

    chunk.chunkChanged()

if __name__ == '__main__':
    main()
