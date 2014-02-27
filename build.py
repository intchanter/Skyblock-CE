#!/bin/env python

import settings
import pymclevel

def main():
    level = pymclevel.MCInfdevOldLevel(settings.output_filename, create=True)
    clear_chunks(level, radius = 0)
    level.saveInPlace()

def clear_chunks(level, radius = 0):
    for chunkX in range(-radius, radius + 1):
        for chunkZ in range(-radius, radius + 1):
            chunk = level.getChunk(chunkX, chunkZ)
            chunk.Blocks[chunk.Blocks != -1] = level.materials.Air.ID
            chunk.chunkChanged()

if __name__ == '__main__':
    main()
