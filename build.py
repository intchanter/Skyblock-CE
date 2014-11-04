#!/usr/bin/env python

import settings
from pymclevel import MCInfdevOldLevel
from pymclevel import TileEntity
try:
    TileEntity.baseStructures['Control']
except KeyError:
    from pymclevel import nbt
    TileEntity.baseStructures['Control'] = (
        ('Command', nbt.TAG_String),
        ('LastOutput', nbt.TAG_String),
    )
from pymclevel import TAG_Compound
from pymclevel import TAG_List
from pymclevel import TAG_Short
from pymclevel import TAG_Byte
from pymclevel import TAG_String
# from pymclevel.mclevelbase import ChunkNotPresent
from pymclevel.items import items

# So we can use relative figures and shift them all around slightly
base = 4


class LevelSlice(object):
    '''
    This allows interacting with a slice of the world without worrying about
    chunk boundaries.
    '''

    # TODO: Try pre-loading all the chunks for the slice and compare that
    # against loading on demand.
    def __init__(self, level, east=0, south=0, up=64, radius=16):
        '''
        up defaults to 64 to allow vertical positions to be specified
        relative to standard overworld sea level.
        '''
        self.level = level
        self.east = east
        self.south = south
        self.up = up
        self.radius = radius
        self.chunks = {}
        self.load()

    def load(self):
        min_east_chunk = (self.east - self.radius) // 16
        max_east_chunk = (self.east + self.radius) // 16
        min_south_chunk = (self.south - self.radius) // 16
        max_south_chunk = (self.south + self.radius) // 16
        for east_chunk in range(min_east_chunk, max_east_chunk + 1):
            for south_chunk in range(min_south_chunk, max_south_chunk + 1):
                self.chunks[east_chunk, south_chunk] = grabChunk(
                    self.level,
                    east_chunk,
                    south_chunk,
                )

    def save(self):
        for chunk in self.chunks:
            self.chunks[chunk].chunkChanged()

    def empty(self):
        self.set_blocks(
            block_id=0,
            minimum=(self.east - self.radius, self.south + self.radius),
            maximum=(self.east - self.radius, self.south + self.radius),
        )

    def set_blocks(self,
                   block_id,
                   block_data=0,
                   minimum=None,
                   maximum=None,
                   ):

        # A very useful shorthand
        if not minimum:
            raise ValueError('set_blocks() requires a minimum point')
        if not maximum:
            raise ValueError('set_blocks() requires a maximum point')
        if len(minimum) == 3:
            min_east, min_south, min_up = minimum
        elif len(minimum) == 2:
            min_east, min_south = minimum
            min_up = 0
        else:
            raise ValueError('set_blocks() received an invalid minimum point')
        if len(maximum) == 3:
            max_east, max_south, max_up = maximum
        elif len(minimum) == 2:
            max_east, max_south = maximum
            max_up = 255
        else:
            raise ValueError('set_blocks() received an invalid maximum point')

        for chunk_east, chunk_south in self.chunks.keys():
            chunk = self.chunks[chunk_east, chunk_south]

            # Don't do anything if this chunk doesn't intersect the region
            if min_east > chunk_east * 16 + 15 or max_east < chunk_east * 16:
                continue
            if (min_south > chunk_south * 16 + 15
                    or max_south < chunk_south * 16):
                continue

            # Normalize relative to this chunk
            c_min_east = min_east % 16
            c_max_east = max_east % 16
            c_min_south = min_south % 16
            c_max_south = max_south % 16
            if min_east < chunk_east * 16:
                c_min_east = 0
            if max_east > chunk_east * 16 + 15:
                c_max_east = 15
            if min_south < chunk_south * 16:
                c_min_south = 0
            if max_south > chunk_south * 16 + 15:
                c_max_south = 15

            chunk.Blocks[
                c_min_east:c_max_east + 1,
                c_min_south:c_max_south + 1,
                min_up:max_up + 1,
            ] = block_id
            chunk.Data[
                c_min_east:c_max_east + 1,
                c_min_south:c_max_south + 1,
                min_up:max_up + 1,
            ] = block_data

    def add_entity(self, entity, position):
        east, south, up = position
        chunk_east = east // 16
        chunk_south = south // 16
        if not (chunk_east, chunk_south) in self.chunks:
            raise KeyError('position not in world slice: {}'.format(position))
        chunk = self.chunks[chunk_east, chunk_south]
        TileEntity.setpos(entity, (east, up, south))
        chunk.TileEntities.append(entity)


def main():
    # Set random_seed explicitly just to avoid randomness
    print('Creating level.')
    level = MCInfdevOldLevel(settings.output_filename,
                             create=True,
                             random_seed=1)
    overworld = level.getDimension(0)
    # Superflat: version 2, one layer of air, deep ocean biome
    overworld.root_tag['Data']['generatorName'] = TAG_String(u'flat')
    overworld.root_tag['Data']['generatorOptions'] = TAG_String(u'2;0;24;')

    nether = level.getDimension(-1)

    the_end = level.getDimension(1)

    if settings.creative:
        level.GameType = level.GAMETYPE_CREATIVE

    # overworld
    print('Generating overworld.')
    create_empty_chunks(overworld, radius=15)
    dirt_island(level, 0, 0)
    sand_island(level, -3, 0)
    bedrock_island(level, 50, -20)
    spawn_island(level, 1000000, 1000000)
    biomify(overworld)

    # nether
    print('Generating nether.')
    nether_radius = 150
    create_empty_chunks(nether, radius=nether_radius)
    create_bedrock_fence(nether, radius=nether_radius)
    soul_sand_island(nether, 0, 0)

    # the_end
    # Manually creating the_end does NOT spawn an ender dragon, so I don't
    # need to figure out how to remove it.
    print('Generating the end.')
    create_empty_chunks(the_end, radius=20)
    obsidian_island(the_end, 6, 0)
    portal_island(the_end, 4, 0)

    print('Finalizing and saving.')
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
    # TODO: Determine if the following call is necessary
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


def create_bedrock_fence(level, radius=0):
    bedrock_id = level.materials.Bedrock.ID
    for chunkX in range(-radius, radius + 1):
        for chunkZ in range(-radius, radius + 1):
            if abs(chunkX) == radius or abs(chunkZ) == radius:
                chunk = grabChunk(level, chunkX, chunkZ)
                chunk.Blocks[:, :, :128] = bedrock_id


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
        {
            'id': items.names['Ice'],
            'count': 1,
            'damage': 0,
        },
        {
            'id': items.names['Lava Bucket'],
            'count': 1,
            'damage': 0,
        },
        signed_book(
            'Book One',
            [
                '''Contents:

2: Credits
3: Basic Objectives ''',  # page 1

                '''Credits:

- Noobcrew made the original Skyblock maps
- Intchanter posted ideas in the Skyblock thread
- WesyWesy suggested Intchanter update Skyblock
- CurtJen and Gaudeon: helped test''',  # page 2

                '''Basic objectives:

- Farm saplings: acacia, birch, dark oak, jungle, oak, spruce
- Farm wheat, melons, pumpkins, cactus, carrots, potatoes
- Farm tall grass, vines, dandelions, poppies''',  # page 3

                '''- Collect arrows, bones, ender pearls, glass bottles
- Collect glowstone dust, gold nuggets, gunpowder, iron, redstone dust,
- Collect rotten flesh, slime balls, spider eyes, string
- Make charcoal
- Generate cobblestone and smooth stone''',  # page 4

                '''- Farm beef, chicken, eggs, feathers, ink sacs
- Farm leather, mutton, pork chops, rabbit, rabbit hide, wool
- Make stone tools
- Milk a cow
- Obtain a rabbit foot
- Craft snow golems
- Make leather armor
- Make cake, pumpkin pie, slime blocks''',  # page 5

                '''- Collect clown fish, fish, lily pads, a nametag
- Collect puffer fish, a daddle, salmon
- Collect a tripwire hook, water bottles''',  # page 6
            ]
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
    chunk.Data[base-1, base+1:base+3, 64:67] = 2

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
        signed_book(
            'Book Two',
            [
                '''Contents:

2: Advanced Objectives
4: Extreme Objectives
6: Crazy Objectives
7: Special Locations''',  # page 1

                '''Advanced Objectives:

- Collect ghast tears, gold
- Obtain records
- Fight or tame a wolf
- Milk a mooshroom
- Farm the other short flowers:
  - red, orange, pink, white tulips
  - oxeye daisy, azure bluet, allium, blue orchid''',  # page 2

                '''- Farm brown and red mushrooms, cocoa beans, nether wart, sugar cane
- Light off a fireworks show''',  # page 3

                '''Extreme Objectives:

- Collect obsidian
- Farm iron
- Farm two-block flowers: sunflower, peony, rose bush, lilac
- Farm ferns
- Brew some potions
- Play a record
- Enchant your own tools and armor
- Make iron armor and tools''',  # page 4

                '''- Cure some villagers
- Obtain emeralds, glass, diamond tools, lapis lazuli, name tags,
saddles, enchanted tools, and armor from villagers
- Collect blaze rods, coal, and wither skeleton heads''',  # page 5

                '''Crazy Objectives:

- Obtain a head from something that isn't a wither skeleton
- Build and kill a wither
- Build a beacon''',  # page 6

                '''Special locations:

Nether fortress: -85x,-78z

End portal: 800x,-160z
''',  # page 7
            ],
        )
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
        {
            'id': items.names['Diamond'],
            'count': 3,
            'damage': 0
        },
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


def spawn_island(level, east, south, target=(6, 6, 64)):
    # TODO: Fill the coordinates based on the actual position of the dirt
    # and spawn islands
    block_radius = 13
    pad_min_east = east - 10
    pad_min_south = south - 10
    pad_max_east = east + 10
    pad_max_south = south + 10
    pad_up = 0  # Bottom of the world so we can't ever spawn below it
    wire_up = pad_up + 1
    redstone_up = wire_up + 1
    cap_up = redstone_up + 1
    slab_id = 126
    slab_data = 0  # oak, lower half
    tripwire_id = 132
    tripwire_data = 4 + 2  # attached and suspended
    tripwire_hook_id = 131
    tripwire_hook_n_data = 4 + 0  # connected, pointing south
    tripwire_hook_s_data = 4 + 2  # connected, pointing north
    redstone_wire_id = 55
    command_block_id = 137
    bedrock_id = 7

    command = u''.join([
        u'/tp',
        u' @p[{s_east},{s_up},{s_south},{radius},c=100]',
        u' {t_east}',
        u' {t_up}',
        u' {t_south}',
    ]).format(
        t_east=target[0],
        t_south=target[1],
        t_up=target[2],
        s_east=east,
        s_south=south,
        s_up=wire_up,
        radius=block_radius,
    )

    # Place the player
    level.setPlayerPosition((east, wire_up + 2, south))
    level.setPlayerSpawnPosition((east, wire_up, south))

    # Get a world slice object
    world_slice = LevelSlice(
        level,
        east=east,
        south=south,
        up=pad_up,
        radius=block_radius,
    )

    world_slice.empty()

    # Slab level
    world_slice.set_blocks(
        block_id=slab_id,
        block_data=slab_data,
        minimum=(pad_min_east, pad_min_south, pad_up),
        maximum=(pad_max_east, pad_max_south, pad_up),
    )

    # Wire level with fully connected tripwire lined N and S with tripwire
    # hooks attached to bedrock
    world_slice.set_blocks(
        block_id=bedrock_id,
        minimum=(pad_min_east, pad_min_south - 2, wire_up),
        maximum=(pad_max_east, pad_max_south + 2, wire_up),
    )
    world_slice.set_blocks(
        block_id=tripwire_hook_id,
        block_data=tripwire_hook_n_data,
        minimum=(pad_min_east, pad_min_south - 1, wire_up),
        maximum=(pad_max_east, pad_min_south - 1, wire_up),
    )
    world_slice.set_blocks(
        block_id=tripwire_hook_id,
        block_data=tripwire_hook_s_data,
        minimum=(pad_min_east, pad_max_south + 1, wire_up),
        maximum=(pad_max_east, pad_max_south + 1, wire_up),
    )
    world_slice.set_blocks(
        block_id=tripwire_id,
        block_data=tripwire_data,
        minimum=(pad_min_east, pad_min_south, wire_up),
        maximum=(pad_max_east, pad_max_south, wire_up),
    )

    # Just above the wire, cap the bedrock on the S and add the redstone
    # wire and command block on the N
    world_slice.set_blocks(
        block_id=slab_id,
        minimum=(pad_min_east, pad_max_south + 2, redstone_up),
        maximum=(pad_max_east, pad_max_south + 2, redstone_up),
    )
    world_slice.set_blocks(
        block_id=redstone_wire_id,
        minimum=(pad_min_east, pad_min_south - 2, redstone_up),
        maximum=(pad_max_east, pad_min_south - 2, cap_up),
    )
    world_slice.set_blocks(
        block_id=command_block_id,
        minimum=(east, pad_min_south - 2, redstone_up),
        maximum=(east, pad_min_south - 2, redstone_up),
    )
    entity = TileEntity.Create('Control')
    entity['Command'] = TAG_String(command)
    entity['LastOutput'] = TAG_String(u'')
    world_slice.add_entity(entity, (east, pad_min_south - 2, redstone_up))

    # Cap redstone wire and command block with slabs
    world_slice.set_blocks(
        block_id=slab_id,
        minimum=(pad_min_east, pad_min_south - 2, cap_up),
        maximum=(pad_max_east, pad_min_south - 2, cap_up),
    )

    world_slice.save()


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
