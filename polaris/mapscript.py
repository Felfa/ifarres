#!/usr/bin/python
from __future__ import print_function, division, unicode_literals

import argparse
import itertools
import sys

import noise
import PIL.Image

def main(width=800, height=600, scale=3, xoffset=0, yoffset=0, num_octaves=6, outfile='/tmp/out.png',
         min_height=-10000, max_height=10000, **kwargs):

  worldmap = [[(0,0,0) for i in range(width)] for i in range(height)]

  freq_mod = scale/width

  for y in range(height):
    for x in range(width):
      nx = x * freq_mod + xoffset
      ny = y * freq_mod + yoffset
      land_level = (max_height - min_height) * (noise.snoise2(nx, ny, octaves=num_octaves) * 0.5 + 0.5) + min_height
      worldmap[y][x] = get_coloring(land_level, min_height, max_height, **kwargs)
  
  im = PIL.Image.new('RGB',(width,height))
  im.putdata(list(itertools.chain(*worldmap)))
  im.save(outfile)

def get_coloring(land_level, min_height, max_height, mode='terrain', **kwargs):
  if mode == 'terrain':
    return terrain_color(land_level, min_height, max_height, **kwargs)
  elif mode == 'height':
    return height_color(land_level, min_height, max_height, **kwargs)
  
def terrain_color(land_level, min_height, max_height, sea_level=1000, sea_color=(0,0,255),
                  coast_color=(0,100,255), shore_color=(244,164,96), land_color=(183,123,72),
                  mountain_color=(122,102,78), coast_diff=1000, shore_diff=1000, mountain_height=15000,
                  **kwargs):
  if land_level > sea_level:
    if land_level - min_height < mountain_height:
      if (land_level - sea_level) < shore_diff:
        return shore_color
      else:
        return land_color
    else:
      return mountain_color
  elif (sea_level - land_level) < coast_diff:
    return coast_color
  else:
    return sea_color

def height_color(land_level, min_height, max_height, **kwargs):
  h = int(2**8 * ((land_level - min_height) / (max_height - min_height)))
  return h, h, h

def color(s):
  if s.startswith('#'):
    ss = s[1:]
    if len(ss) == 3:
      return tuple(int(c * 2, base=16) for c in ss)
    elif len(ss) == 6:
      return tuple(int(ss[i:i+2], base=16) for i in range(0, len(ss), 2))
    else:
      raise ValueError('Invalid literal "{}" for hexidecimal color'.format(s))
  else:
    r,g,b = tuple(min(max(int(i), 0), 255) for i in s.replace(':', ',').split(','))
    return r, g, b
  
if __name__ == '__main__':
  parser = argparse.ArgumentParser(add_help=False, description='Generate terrain maps')
  parser.add_argument('-H', '--help', action='store_true', help='Show this message and exit')

  parser.add_argument('-w', '--width', type=int, help='Width of the final image')
  parser.add_argument('-h', '--height', type=int, help='Height of the final image')
  parser.add_argument('-s', '--scale', type=float, help='Scale of the map')
  parser.add_argument('-x', '--xoffset', type=float, help='Offset to apply to the horizontal noise position')
  parser.add_argument('-y', '--yoffset', type=float, help='Offset to apply to the vertical noise position')
  parser.add_argument('-S', '--sea-level', type=float, help="How high should the map's sea level be")

  parser.add_argument('-O', '--num-octaves', type=int, help='How many octaves to use')

  parser.add_argument('--min-height', type=float, help='Lowest possible map point')
  parser.add_argument('--max-height', type=float, help='Hightest possible map point')
  
  parser.add_argument('--sea-color', type=color, help='Color for deep water')
  parser.add_argument('--coast-color', type=color, help='Color for water near land')
  parser.add_argument('--shore-color', type=color, help='Color for land near water')
  parser.add_argument('--land-color', type=color, help='Color for land')
  parser.add_argument('--mountain-color', type=color, help='Color for mountains')

  parser.add_argument('--coast-diff', type=float, help='Height limit from shore for coast')
  parser.add_argument('--shore-diff', type=float, help='Height limit from coast for shore')
  parser.add_argument('--mountain-height', type=float, help='Height at which to make mountains')

  parser.add_argument('-m', '--mode', type=str, choices=('terrain', 'height'),
                      help='Type of map to generate')

  parser.add_argument('-o', '--outfile', type=str, help='File to write the map image to')
  
  args = {k:v for k,v in vars(parser.parse_args()).items() if v is not None}

  if args['help']:
    parser.print_help()
    sys.exit(0)
  else:
    del args['help']
  
  main(**args)
