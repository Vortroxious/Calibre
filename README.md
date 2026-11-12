# Calibre: realistic firearms for Minecraft 1.21.11 (NeoForge and Fabric) + GeckoLib 5

Calibre is a gun mod with 77 real-world firearms. Every gun has fully animated first-person handling built on GeckoLib 5.4.5:
- a draw, fire and dry-fire animation
- a tactical and an empty reload
- fire-mode switching
- bolt/pump cycling where the gun has a manual action
- an inspect animation that is different for every gun

It also includes:
- projectile ballistics with drop, travel time and penetration
- 14 attachments
- a gunsmithing workbench
- an armed hostile mob
- chest loot

## Installing
Pick the jar for your loader. GeckoLib 5.4.5 is bundled inside both (jar-in-jar), so you don't install it separately. If you also have a newer GeckoLib 5.x installed, the loader uses the newer one.

| Loader | Jar | You also need |
|---|---|---|
| NeoForge 21.11.48+ | `calibre-neoforge-1.2.0.jar` | nothing else |
| Fabric Loader 0.18+ | `calibre-fabric-1.2.0.jar` | [Fabric API](https://modrinth.com/mod/fabric-api). [Mod Menu](https://modrinth.com/mod/modmenu) is optional and adds an in-game settings screen. |

Both versions have the same guns, animations, sounds, attachments, workbench, mobs and loot. A server and its players must use the same loader's jar.

## The guns
| Class | Guns |
|---|---|
| Pistols | Glock 17 (9mm), M1911A1 (.45 ACP), Beretta M9 (9mm), Desert Eagle (.50 AE) |
| Revolver | S&W Model 29 (.44 Magnum), speedloader reload |
| SMGs | H&K MP5A3, H&K UMP45, IMI Uzi (open bolt), FN P90 (top-mounted mag) |
| Assault rifles | Colt M4A1, H&K HK416, AKM, Steyr AUG A3 |
| Battle rifles / DMRs | FN FAL, FN SCAR-H, SVD Dragunov (integral PSO-1), M14 EBR |
| Snipers | M24 SWS (bolt, internal mag, loaded round by round), AI AWM, Barrett M82A1 |
| Shotguns | Remington 870 (pump, loaded shell by shell), Benelli M4 |
| LMGs | FN M249 SAW, PKM (belt-fed: feed cover, box swap, belt seat) |
| Launcher | RPG-7 (PG-7V rocket: arming distance, sustainer motor) |
| WWII / Cold War | Mosin-Nagant M91/30, M1917 Enfield, Arisaka Type 99 (bolt actions loaded with **stripper clips**), SKS (two clips into its fixed magazine), PPSh-41 (71-round drum), Carl Gustaf m/45 "Swedish K", AK-47 (milled receiver) |
| Lever actions | Winchester Model 1894, Marlin 336 (lever throw cycles the bolt and cocks the hammer, side loading gate) |
| Hunting / precision | Tikka T3 (.30-06, scoped), Savage Model 10 (.300 Blackout, scoped, threaded) |
| More shotguns | Winchester Model 12 trench gun (**slam fire**: hold the trigger and it fires every time the slide closes), Benelli Nova, Charles Daly 300 Field, Mossberg 190 (16-gauge bolt-action with box magazine) |
| More handguns | Walther PPQ, Bersa Thunder 380, Ruger Mark III (.22), S&W 642 Airweight (.38 snub, speedloader), Ruger Single-Six (**single action**: thumb-cock every shot, loaded one chamber at a time through the gate) |

| Modern | Kriss Vector (.45, 2-round burst), H&K MP7A1 (4.6×30), H&K G36C, FAMAS F1 (bullpup), IWI Tavor X95 (bullpup), FN Five-seveN, H&K USP, CZ 75 SP-01, Franchi SPAS-12 (pump), Atchisson AA-12 (full-auto shotgun) |
| WWII | Karabiner 98k and Lee-Enfield No.4 (stripper clips), M1 Garand (8-round en-bloc clip that **pings** out on the last shot), Thompson M1A1, MP40, StG 44, MG42 (belt-fed, 1200 rpm), M1918 BAR |
| Sniper / precision | CheyTac M200 Intervention (.408), AI L96A1, Remington 700 (internal magazine, loaded round by round), KAC SR-25, SVU (bullpup Dragunov), DSR-1 (bullpup, .338 Lapua) |
| Cold War | M60 (belt-fed), M16A1, IMI Galil ARM, H&K G3A3 (HK slap), Sten Mk II (**side-mounted magazine**), Colt Python (.357), Skorpion vz. 61 (.32 ACP), KS-23 (23 mm pump) |

The 20 guns from Lever actions to More handguns each fire their **own recorded gunshot** from the Free Firearm Sound Library. The 32 guns in the last four rows use the closest of those recordings, re-pitched for their calibre and mastered for their class.

### Models
Every gun is modelled to its real overall and barrel length (the build fails a gun that is more than 6 % off), with rounded edges and barrels, iron sights you actually look through, cartridges you can see in magazines, clips and belts, and small parts that move: safeties, magazine releases, slide stops and bolt catches, bolt shrouds that slide without turning, dust covers. A typical gun has about 440 parts; the scoped sniper rifles have around 1,000.

That detail is for the gun in your own hands. Anywhere else (other players, mercenaries, inventory icons, item frames, guns lying on the ground) the mod draws a simplified version of the same gun with about a quarter of the parts, so a crowd of armed mobs or a creative tab full of guns costs no more than it did before.

Stats come from the real weapons:
- magazine capacity, plus one round in the chamber for closed-bolt guns
- cyclic rate
- muzzle velocity, which drives bullet travel time and drop
- available fire modes
- weight, which affects aim time and sway

Ammunition comes in 32 calibres.

### Inspects (H)
Every inspect is a close-up presentation (in the style of modern shooters such as MW3) of about 7–9 seconds,
generated from each gun's own parts (`tools/calibre_gen/cs2.py`):
- **Long guns:** snapped up to the eye side-on with the muzzle up and held, the magazine pulled out and brought up to the camera to look at the rounds (the gun drops away meanwhile) and pushed home, turned over to the other side, a press-check with whatever the gun has (charging handle, bolt, pump, lever or feed cover), a selector flick, back to ready.
- **Pistols:** the slide side-on up close, a press-check, the other side, the magazine shown to the camera, a look along the top of the slide.
- **Revolvers:** the cylinder swung out and spun (or the gate opened and the cylinder clicked round), both sides held up close.

Handling sounds come from real recordings, and the camera moves subtly with every weapon action (the **Camera motion** setting).

## Controls
| Action | Key |
|---|---|
| Fire | Left mouse button |
| Aim down sights | Hold right mouse button. Right-clicking a block still interacts with it, such as the workbench. |
| Reload | R. Firing interrupts a shell-by-shell or clip reload. |
| Fire mode | V |
| Inspect | H |

- Crouching lowers spread and recoil, especially with a bipod or an LMG.
- Sprinting lowers the gun and blocks firing.

## Systems
- **Ballistics:**
  - Bullets are real entities that are ray-cast every tick, with gravity and drag.
  - Headshots deal ×2 (configurable). Damage falls off with range. Some calibres pierce armor.
  - Rounds over-penetrate soft targets.
  - Bullets shatter glass, pass through leaves and wood, and .50 BMG goes through masonry.
  - Impacts make particles and material sounds.
  - Supersonic rounds make a "whiz" for players they pass close to.
  - Tracers appear on every 5th round (every 3rd for LMGs).
- **Attachments:**

  | Slot | Attachments |
  |---|---|
  | Optics | red dot, holographic, ACOG 4×, 8× scope, PSO-1 |
  | Muzzle | pistol suppressor, rifle suppressor, compensator, flash hider |
  | Underbarrel | vertical grip, angled grip, bipod |
  | Other | laser, extended magazine |

  - Each attachment changes recoil, spread, aim time and zoom. Suppressors remove the muzzle flash and the loud report.
  - Optics of 4× and above use a full-screen reticle overlay (mil-dot, PSO-1 chevrons, ACOG) and reduce mouse sensitivity.
- **Gun Workbench:**
  - Craft it from iron, redstone, planks and a crafting table.
  - The Guns, Ammo and Parts tabs craft directly from your inventory.
  - The Modify tab installs and removes attachments on the gun in your hand.
- **Mercenaries** spawn at night in the Overworld:
  - Each carries a random real gun.
  - They fire in bursts, strafe and reload.
  - They drop ammo, and rarely their gun or an attachment.
- **Loot:** guns, ammo and attachments appear in these chests:
  - weaponsmith, pillager outpost and shipwreck
  - dungeons, mineshafts and temples
  - strongholds and mansions
  - bastions, ancient cities, End cities and trial chambers
- **HUD:** ammo count and reserve, round pips, calibre, fire mode, a spread-driven dynamic crosshair, and hit/headshot/kill markers.
- **Config:**
  - Server: damage and headshot multipliers, glass breaking, explosion griefing, infinite ammo, tracers, mercenary spawns.
  - Client: HUD, crosshair, sway, bob, camera recoil, camera motion, ADS sensitivity.
  - NeoForge: Mods → Calibre → Config (per-world server config + client config).
  - Fabric: `config/calibre-server.json` and `config/calibre-client.json`, or Mod Menu → Calibre → Config.

## How the assets are made
All models, textures, animations and sounds are **generated** by the Python tools in `tools/`. Their output is committed (in `common/`), so building the mod does not need Python.

| Script | What it does |
|---|---|
| `tools/build_assets.py [gun] [--preview]` | Gun and attachment models (GeckoLib geo), textures, animations, and per-gun timing metadata. |
| `tools/gen_sounds.py` | Synthesizes fallback versions of every sound (numpy + ffmpeg). |
| `tools/import_sounds.py <src>` | Replaces the gunshots and reload/handling sounds with cuts of real **CC0 recordings** (mapping in `tools/sound_map.json`, sources and checksums in `tools/sound_sources.tsv`, see `CREDITS.md`). Run it after `gen_sounds.py`. |
| `tools/gen_data.py` | Item model JSONs, lang, loot, damage types, the biome modifier, block assets, GUI and effect textures. |
| `tools/validate.py` | Checks the bone and animation contract, sound references, UVs and item files, and that every gun has at least 130 parts and is within 6 % of its real length (`tools/rosters/specs.py`). |

How the pieces fit together:
- Models are authored in millimetres from real dimensions, with a small cuboid DSL (`tools/calibre_gen/core.py`) and shared kits for each family (`parts.py`, `pistolkit.py`, `longkit.py`, `riflekit.py`, `shotkit.py`). Rounded edges and tubes are built from facets lit by their own normals.
- Each gun is built twice: in full, and with `core.LOD` switched on (plain boxes, octagonal tubes, no small trim) for the `<id>_lod` model the renderer uses outside first person.
- Animations are authored as eased keyframe "beats" with springs and shakes, plus a `grab` constraint that makes a hand follow the magazine, slide or bolt it is holding. They are baked to GeckoLib keyframes (`templates.py` and `guns/*.py`).
- The same generator writes `calibre_gen/guns/<id>.json` with every animation's length, sound timeline and the moment the round goes in. The server uses it to time reloads, so the game logic always matches the animation.
- `--preview` renders side, iso and first-person views and per-animation frame sheets to `build/preview/`.

You can open the generated `.geo.json` / `.animation.json` files in Blockbench (GeckoLib plugin) to tweak them by hand. To swap a sound, change its line in `tools/sound_map.json` and re-run `tools/import_sounds.py`, or drop in your own `.ogg` and point `assets/calibre/sounds.json` at it.

## Project layout
| Folder | What's in it |
|---|---|
| `common/` | Everything shared by both loaders: guns, ballistics, animations logic, rendering, HUD, workbench, mobs, and all generated assets (models, textures, animations, sounds, data). Loader-specific calls go through `dev.calibre.platform.Platform`. |
| `neoforge/` | NeoForge glue: event wiring, ModConfigSpec config, global loot modifiers, the biome modifier, GameTest registration. |
| `fabric/` | Fabric glue: Fabric API wiring, mixins for the first-person hand, FOV, mouse sensitivity, click handling and arm pose, the JSON config + Mod Menu screen, loot and spawn hooks, gametest wrappers. |
| `tools/` | The asset generators. They write into `common/` (and NeoForge-only data into `neoforge/`). |

## Building and testing
```bash
./gradlew buildAll
```
This builds both jars and copies `calibre-neoforge-1.2.0.jar` and `calibre-fabric-1.2.0.jar` to the project root. It needs Gradle 9.2+ (the wrapper downloads it) and Java 21.

```bash
./gradlew :neoforge:runGameTestServer
```
```bash
./gradlew :fabric:runGametest
```
These run the same GameTests on each loader: bullet damage, headshots, glass penetration, round consumption, every gun's animation set, recipes, reload timing, stripper clips (Mosin and SKS), lever cycling and single-action gate loading.

```bash
./gradlew :neoforge:runClient
```
```bash
./gradlew :fabric:runClient
```
These start a normal dev client.

```bash
./gradlew :neoforge:runAutotest
```
```bash
./gradlew :fabric:runAutotest
```
These are scripted client runs. They create a flat world, cycle through guns, the workbench and the settings screen, and write screenshots to `<loader>/run/screenshots/`. Add `-PautotestGuns=mosin,sks,...` to tour specific guns instead (hip, ADS, empty reload, fire and inspect for each).

## License
Calibre is **All Rights Reserved** (see `LICENSE`). The bundled GeckoLib is MIT. The sound recordings are CC0, except
the clips cut from "Handling Guns" by Gary, which are CC-BY-SA 3.0 (see `CREDITS.md`).

## Publishing to Modrinth
```bash
python3 tools/modrinth_publish.py publish --dry-run
```
```bash
./gradlew publishModrinth
```
The first command checks everything without uploading. The second builds both jars and publishes them; it needs a
Modrinth Personal Access Token in the `MODRINTH_TOKEN` environment variable. The page text, icon and gallery live in
`tools/modrinth/`; `tools/make_icon.py` regenerates the icon.

