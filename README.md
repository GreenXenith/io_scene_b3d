# io_scene_b3d

Blender Import-Export script for Blitz 3D .b3d files.\
Should work with versions 2.8x, 2.9x, 3.x, and 4.x.

## Installation
Download the ZIP file:
* [Master](https://github.com/GreenXenith/io_scene_b3d/archive/refs/heads/master.zip)
* [Latest release](https://github.com/GreenXenith/io_scene_b3d/releases/latest/)
* [All releases](https://github.com/GreenXenith/io_scene_b3d/releases)  

Then follow the add-on installation instructions for your Blender version:
* [2.8x](https://docs.blender.org/manual/en/2.80/editors/preferences/addons.html#rd-party-add-ons)
* [2.9x](https://docs.blender.org/manual/en/2.90/editors/preferences/addons.html#installing-add-ons)
* [3.x](https://docs.blender.org/manual/en/3.0/editors/preferences/addons.html#installing-add-ons)
* [Latest](https://docs.blender.org/manual/en/latest/editors/preferences/addons.html#installing-add-ons)

## TODO
### Import
* Animation is not yet implemented in version 1.0. Check master branch for updates.
* Nodes use original quaternion rotation that affects user interface.
Maybe convert them into euler angles.

## History
Blitz3D was a game engine developed by Blitz Research (Mark Sibly) in 2001 utilizing the Blitz BASIC language and bringing with it the B3D format.  
[Source](https://github.com/blitz-research/blitz3d) | [Website](https://web.archive.org/web/20170724000113/http://www.blitzbasic.com/) | [Wikipedia](https://en.wikipedia.org/wiki/Blitz_BASIC)  

Blender addon:
* 2008 - Developed for Blender 2.45 by Diego "GaNDaLDF" Parisi
* 2010 - Lightmap fixes by Capricorn 76 Pty. Ltd (date estimated)
* 2011 - Changes by Marianne Gagnon and Joerg Henrichs from supertuxkart
* 2013 - Blender 2.62 and 2.63 compatibility work from MTLZ (aka "is06", date estimated)
* 2018 - Blender 2.8 compatibility and importer by Joric
* 2020 - Blender 2.9 compatibility by GreenXenith
* 2023 - Blender 3.0 compatibility by GreenXenith

## License
This software is covered by [GPL 2.0](LICENSE). Pull requests are welcome.

* The import script based on a heavily rewriten (new reader) script from Glogow Poland Mariusz Szkaradek.
* The export script uses portions of script by Diego 'GaNDaLDF' Parisi (ported to Blender 2.8) under GPL license.
* The b3d format documentation (b3dfile_specs.txt) doesn't have a clear license (Public Domain assumed).

## Alternatives
* [Original addon by Joric](https://github.com/joric/io_scene_b3d) - Works for Blender 2.8 but not later
* [B3DExport by RainWarrior](https://github.com/RainWarrior/B3DExport) - Based on same work from Diego Parisi, for Blender 2.6 or 2.7
* [B3DExport for Minetest](https://github.com/minetest/B3DExport) - Minetest's fork of B3DExport for Blender 2.7
* [Assimp](https://github.com/assimp/assimp) - Importer only. Animation is allegedly hit-or-miss
* [fragMOTION](http://www.fragmosoft.com/fragMOTION/index.php) - Seems to work fine, though it is nagware and does not export animation to any modern formats
