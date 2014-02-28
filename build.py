#!/bin/env python

import settings
import pymclevel

def main():
    level = pymclevel.MCInfdevOldLevel(settings.output_filename, create=True)
    clear_chunks(level, radius = 0)
    dirt_island(level)
    level.saveInPlace()

def clear_chunks(level, radius = 0):
    for chunkX in range(-radius, radius + 1):
        for chunkZ in range(-radius, radius + 1):
            chunk = level.getChunk(chunkX, chunkZ)
            chunk.Blocks[:, :, :] = level.materials.Air.ID
            #chunk.Blocks[chunk.Blocks != -1] = level.materials.Air.ID
            chunk.chunkChanged()

def dirt_island(level):
    chunk = level.getChunk(0, 0)
    chunk.Blocks[0:4, 0:4, 64:68] = level.materials.Dirt.ID
    chunk.Blocks[4:8, 0:4, 64:68] = level.materials.Dirt.ID
    chunk.Blocks[0:4, 4:8, 64:68] = level.materials.Dirt.ID
    chunk.chunkChanged()

if __name__ == '__main__':
    main()
