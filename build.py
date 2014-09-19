#!/bin/env python

import settings
from pymclevel import MCInfdevOldLevel
from pymclevel import TileEntity
from pymclevel import TAG_Compound
from pymclevel import TAG_List
from pymclevel import TAG_Short
from pymclevel import TAG_Byte
from pymclevel import TAG_String
from pymclevel.mclevelbase import ChunkNotPresent
from pymclevel.items import items

# So we can use relative figures and shift them all around slightly
base = 4


def main():
    # Set random_seed explicitly just to avoid randomness
    level = MCInfdevOldLevel(settings.output_filename,
                             create=True,
                             random_seed=1)
    overworld = level
    # Superflat: version 2, one layer of air, deep ocean biome
    overworld.root_tag['Data']['generatorName'] = TAG_String(u'flat')
    overworld.root_tag['Data']['generatorOptions'] = TAG_String(u'2;0;24;')

    nether = level.getDimension(-1)

    the_end = level.getDimension(1)

    if settings.creative:
        level.GameType = level.GAMETYPE_CREATIVE

    # Place the player
    px, py, pz = (6, 64, 6)
    level.setPlayerPosition((px, py + 2, pz))
    level.setPlayerSpawnPosition((px, py, pz))

    create_empty_chunks(overworld, radius=15)
    create_empty_chunks(nether, radius=150)
    create_empty_chunks(the_end, radius=20)

    # overworld
    dirt_island(level, 0, 0)
    sand_island(level, -3, 0)
    bedrock_island(level, 1, 0)

    # nether
    soul_sand_island(nether, 0, 0)

    # the_end
    # Manually creating the_end does NOT create an ender dragon, so I don't
    # need to figure out how to remove it.
    obsidian_island(the_end, 6, 0)
    portal_island(the_end, 4, 0)

    biomify(overworld)
    level.generateLights()
    level.saveInPlace()


def item_stack(item):
    item_tag = TAG_Compound()
    item_tag.name = 'tag'
    item_tag['id'] = TAG_Short(item['id'])
    item_tag['Damage'] = TAG_Short(item['damage'])
    item_tag['Count'] = TAG_Byte(item['count'])
    item_tag['Slot'] = TAG_Byte(item['slot'])
    return item_tag


def signed_book(title='', pages=[''], author='Skyblock CE'):
    book_tag = TAG_Compound()
    book_tag.name = 'tag'
    book_tag['title'] = title
    book_tag['author'] = author
    book_tag['pages'] = TAG_List(name='pages', list_type=TAG_String)
    for page in pages:
        book_tag['pages'].append(TAG_String(page))
    item_tag = TAG_Compound()
    item_tag['id'] = TAG_Short(items.names['Written Book'])
    item_tag['Damage'] = TAG_Byte(0)
    item_tag['Count'] = TAG_Byte(1)
    item_tag['tag'] = book_tag
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
        try:
            item.name  # Already a TAG_Compound?
            item['Slot'] = TAG_Byte(slot)
            chest['Items'].append(item)
        except AttributeError:
            item['slot'] = slot
            chest['Items'].append(item_stack(item))
        slot += 1
    chunk.TileEntities.append(chest)


def grabChunk(level, chunkX, chunkZ):
    try:
        level.createChunk(chunkX, chunkZ)
    except ValueError:
        pass
    chunk = level.getChunk(chunkX, chunkZ)
    chunk.chunkChanged()
    return chunk


def clear(level, chunkX, chunkZ):
    chunk = grabChunk(level, chunkX, chunkZ)
    chunk.Blocks[:, :, :] = 0  # air_id
    chunk.Biomes[:, :] = -1  # not yet calculated
    chunk.chunkChanged()
    return chunk


def create_empty_chunks(level, radius=0):
    for chunkX in range(-radius, radius + 1):
        for chunkZ in range(-radius, radius + 1):
            level.createChunk(chunkX, chunkZ)


def dirt_island(level, chunkX, chunkZ):
    # Main
    clear(level, chunkX, chunkZ)
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
        signed_book(
            'Welcome to Skyblock CE!',
            ['Page 1',
                'Page 2']
            ),
        ]
    chunkX *= 16
    chunkZ *= 16
    make_chest(level, chunk, (chunkX+base+7, chunkZ+base+2, 64), contents)


def sand_island(level, chunkX, chunkZ):
    # Main
    clear(level, chunkX, chunkZ)
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
        # {'id': items.names['Melon Slice'],
        {'id': 360,  # items.names['Melon'],
            'count': 1, 'damage': 0},
        {'id': items.names['Spruce Sapling'],
            'count': 2, 'damage': 1},
        {'id': items.names['Pumpkin Seeds'],
            'count': 1, 'damage': 0},
        signed_book(
            'Sand Island Objectives',
            ["Now that you've reached the sand island, new objectives"
                + " are possible:\n\n",
                '',
                ''],
            )
    ]
    # Entities need the world-wide coordinates?!
    chunkX *= 16
    chunkZ *= 16
    make_chest(level, chunk, (chunkX+base+3, chunkZ+base+3, 64), contents)

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
        {'id': 6,  # items.names['Dark Oak Sapling'],
            'count': 2, 'damage': 5},
        {'id': items.names['Birch Sapling'],
            'count': 2, 'damage': 2},
        {'id': items.names['Sugar Canes'],
            'count': 1, 'damage': 0},
        ]
    chunkX *= 16
    chunkZ *= 16
    make_chest(level, chunk, (chunkX+base+3, chunkZ+base+3, 64), contents)

    # Mushrooms and Netherwart
    red_mushroom_id = level.materials.RedMushroom.ID
    brown_mushroom_id = level.materials.BrownMushroom.ID
    netherwart_id = level.materials.NetherWart.ID
    chunk.Blocks[base+3, base, 64] = red_mushroom_id
    chunk.Blocks[base, base+3, 64] = brown_mushroom_id
    chunk.Blocks[base, base, 64] = netherwart_id

    chunk.chunkChanged()


def bedrock_island(level, chunkX, chunkZ):
    clear(level, chunkX, chunkZ)
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
        {'id': items.names['Fern'],
            'count': 1, 'damage': 2},
        {'id': 175,  # items.names['Sunflower'],
            'count': 1, 'damage': 0},
        {'id': 175,  # items.names['Lilac'],
            'count': 1, 'damage': 1},
        {'id': 175,  # items.names['Rose Bush'],
            'count': 1, 'damage': 4},
        {'id': 175,  # items.names['Peony Bush'],
            'count': 1, 'damage': 5},
        {'id': 6,  # items.names['Acacia Sapling'],
            'count': 2, 'damage': 4},
        {'id': 6,  # items.names['Jungle Sapling'],
            'count': 2, 'damage': 3},
        {'id': items.names['Cocoa Beans'],
            'count': 1, 'damage': 3},
        ]
    chunkX *= 16
    chunkZ *= 16
    make_chest(level, chunk, (chunkX+base+3, chunkZ+base+3, 1), contents)

    # Light this so it's less likely that something will go terribly wrong and
    # destroy the chest.  Also, stop stealing spawning slots.
    torch_id = level.materials.Torch.ID
    chunk.Blocks[base+4, base+4, 1] = torch_id

    chunk.chunkChanged()


def obsidian_island(level, chunkX, chunkZ):
    # End
    chunk = level.getChunk(chunkX, chunkZ)
    chunk2 = level.getChunk(chunkX, chunkZ - 1)

    # Obsidian
    # When the player is teleported to the_end, it appears that they go to
    # a fixed point at X:100,Y:49(foot),Z:0.
    obsidian_id = level.materials.Obsidian.ID
    air_id = level.materials.Air.ID
    chunk.Blocks[base-2:base+3, 0:base-1, 44:49] = obsidian_id
    chunk2.Blocks[base-2:base+3, base-6:, 44:49] = obsidian_id
    chunk.Blocks[base-1:base+2, 0:base-2, 45:48] = air_id
    chunk2.Blocks[base-1:base+2, base-5:, 45:48] = air_id

    contents = [
        {'id': items.names['Diamond'],
            'count': 3, 'damage': 0},
        signed_book(
            'Credits',
            ["",
                ''],
            )
        ]
    chunkX *= 16
    chunkZ *= 16
    make_chest(level, chunk, (chunkX+base, chunkZ+base-4, 45), contents)

    chunk.chunkChanged()


def portal_island(level, chunkX, chunkZ):
    # End
    chunk = level.getChunk(chunkX, chunkZ)

    # Bedrock frame
    bedrock_id = level.materials.Bedrock.ID
    chunk.Blocks[base-2:base+3, base-1:base+2, 47] = bedrock_id
    chunk.Blocks[base-1:base+2, base-2:base+3, 47] = bedrock_id
    chunk.Blocks[base-1:base+2, base-3:base+4, 48] = bedrock_id
    chunk.Blocks[base-2:base+3, base-2:base+3, 48] = bedrock_id
    chunk.Blocks[base-3:base+4, base-1:base+2, 48] = bedrock_id

    # Portal
    portal_id = level.materials.EnderPortal.ID
    chunk.Blocks[base-2:base+3, base-1:base+2, 48] = portal_id
    chunk.Blocks[base-1:base+2, base-2:base+3, 48] = portal_id

    # Bedrock spire
    chunk.Blocks[base, base, 47:52] = bedrock_id

    # Torches
    torch_id = level.materials.Torch.ID
    (chunk.Blocks[base+0, base-1, 50],
        chunk.Data[base+0, base-1, 50]) = (torch_id, 4)
    (chunk.Blocks[base+1, base+0, 50],
        chunk.Data[base+1, base+0, 50]) = (torch_id, 1)
    (chunk.Blocks[base+0, base+1, 50],
        chunk.Data[base+0, base+1, 50]) = (torch_id, 3)
    (chunk.Blocks[base-1, base+0, 50],
        chunk.Data[base-1, base+0, 50]) = (torch_id, 2)

    # Dragon Egg
    dragon_egg_id = level.materials.DragonEgg.ID
    chunk.Blocks[base, base, 52] = dragon_egg_id

    chunk.chunkChanged()


def biomify(level):
    desired_biomes = [
        10,  # Frozen Ocean
        10,  # Frozen Ocean
        26,  # Cold Beach
        4,  # Forest
        27,  # Birch Forest
        132,  # Flower Forest
        21,  # Jungle
        5,  # Taiga
        6,  # Swampland
        129,  # Sunflower Plains
        35,  # Savannah
        1,  # Plains
        16,  # Beach
        0,  # Ocean
        14,  # Mooshroom Island
        0,  # Ocean
    ]
    radius = len(desired_biomes) - 1
    for chunkZ in range(-radius, radius + 1):
        for chunkX in range(-radius, radius + 1):
            chunk = level.getChunk(chunkX, chunkZ)
            biome = desired_biomes[max(abs(chunkX), abs(chunkZ))]
            chunk.Biomes[:, :] = biome
            chunk.chunkChanged()

if __name__ == '__main__':
    main()
