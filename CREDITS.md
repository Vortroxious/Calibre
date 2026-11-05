# Credits

## Sound recordings
Gunshots and reload / handling sounds are cut from these recordings. All of them except "Handling Guns" (below) are
released under **CC0 1.0 (public domain)** on OpenGameArt, so they need no attribution — credited here anyway, with thanks.
`tools/import_sounds.py` + `tools/sound_map.json` show exactly which cut of which file each in-game sound uses;
`tools/sound_sources.tsv` lists every downloaded file with its SHA-256.

| Pack | Author (OpenGameArt) | Used for |
|---|---|---|
| [The Free Firearm Sound Library](https://opengameart.org/content/the-free-firearm-sound-library) | Ben Jaszczak, et al. (submitted by bart) | All gunshots. Every recorded gun is also in the mod with its own report: Walther PPQ, Bersa, Ruger Mark III, S&W 642, Ruger Single Six, Carl Gustav M45, PPSh, AK-47, SKS, Springfield 1917, Arisaka, Mosin-Nagant, Tikka T3, Savage 10, Winchester 1894, Marlin 336, Winchester Model 12, Charles Daly, Benelli Nova, Mossberg 190 (the 1911 and AR-15 recordings voice the M1911 and the AR-family rifles) |
| [Gun reload sounds](https://opengameart.org/content/gun-reload-sounds) | springyspringo | Rifle and pistol magazine in/out, slide release, bolt/pump, stripper clip strip, drum in/out, lever |
| [Gun Reload Sound Effects](https://opengameart.org/content/gun-reload-sound-effects) | bmaczero | Magazine seat clicks, single-round insert, clip seat, loading gate |
| [Handgun Reload Sound Effect](https://opengameart.org/content/handgun-reload-sound-effect) | zer0sol | Pistol mag release / insert, slide rack |
| [Shotgun Reload Sound effects](https://opengameart.org/content/shotgun-reload-sound-effects) | zer0sol | Shell inserts, pump rack, bolt close |
| [Equipment Clicks II](https://opengameart.org/content/equipment-clicks-ii) and [III](https://opengameart.org/content/equipment-clicks-iii) | lfa | Selector, safety, dust cover, latches, small clicks |
| [Hollywood-style pistol silencer sound effect](https://opengameart.org/content/hollywood-style-pistol-silencer-sound-effect) | bart | Suppressed shots |
| [Fabric Rustling](https://opengameart.org/content/fabric-rustling) | Iochi Glaucus | Cloth / sleeve rustle (inspect, draw) |
| [202 More Sound Effects](https://opengameart.org/content/202-more-sound-effects) | OwlishMedia | Cloth rustle |
| [50 RPG sound effects](https://opengameart.org/content/50-rpg-sound-effects) | Kenney | Cloth, leather grips, belt / pouch handling |
| [RPG Sound Pack](https://opengameart.org/content/rpg-sound-pack) | artisticdude | Finger-spin swish, cloth |

### CC-BY-SA 3.0
| Pack | Author (OpenGameArt) | Used for |
|---|---|---|
| [Handling Guns](https://opengameart.org/content/handling-guns) | Gary (recorded for PARPG) | The gun's own rattle when it is turned in the hands (`handle_rifle`, `handle_pistol`, `handle_heavy`), hand grips (`grip`), the magazine wiggle (`mag_check`) and the click in the draw sounds |

The clips cut from "Handling Guns" (`assets/calibre/sounds/real/handle_*`, `grip_3`–`grip_5`, `mag_check_*`, and the
`draw_pistol` / `draw_rifle` mixes) are adaptations of Gary's recordings and are themselves licensed
**CC-BY-SA 3.0** (https://creativecommons.org/licenses/by-sa/3.0/). The rest of the mod is not affected.

Not used: the "Gunshot Sounds" pack — its OpenGameArt page says CC0 but the archive's own licence file says
CC-BY 3.0, so it was left out to be safe.

The revolver cylinder ratchet (`cylinder_spin`) is a train of real clicks from Equipment Clicks II/III.
Impacts, hit markers, the ejector rod and the bullet whiz are still synthesized by `tools/gen_sounds.py`.

## Libraries
- [GeckoLib](https://github.com/bernie-g/geckolib) 5 (MIT) — animation engine, bundled inside the jar.
