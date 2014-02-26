#!/bin/env python

import settings
import pymclevel

def main():
    level = pymclevel.MCInfdevOldLevel(settings.output_filename, create=True)
    print level

if __name__ == '__main__':
    main()
