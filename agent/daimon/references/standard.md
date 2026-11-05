# Realism QA standard

The bar: **a viewer only learns it is AI if the creator tells them.** If a sharp-eyed viewer, a
client, or a commenter zooming in on a phone could point at something and say "AI", it fails.

## 1. Pick the mode first (ask if the brief does not make it obvious)

| Mode | What must be real | What may look CG | Fails on |
|---|---|---|---|
| **Photoreal** | Everything: people, places, objects, light | Nothing | Any AI tell or hallucination anywhere |
| **Hybrid** | People (skin, hands, eyes, hair, cloth, how they move) and anything they touch | Environments, set extensions, creatures, sci-fi elements, as long as they are lit and grounded like a real VFX shot | Any AI tell on a person; any CG element that is not lit, shadowed, focused and grained like the plate |
| **3D / stylized** | Nothing has to look photographed | All of it | Hallucinations only: broken geometry, wrong counts, melting, gibberish text, continuity breaks, physics that contradicts the style's own rules |

## 2. Severity (zero tolerance)

- **FAIL**: anything that would make a viewer suspect AI, or any hallucination. One FAIL = the whole piece fails, no matter the score.
- **POLISH**: a craft note that makes it better but would not give it away (story logic, composition, grade).
- **STRENGTH**: something that already sells it. Always record these too; the report shows good and bad.

Every FAIL and POLISH needs: where it is (marker x/y in % of the frame, timecode for video), what is wrong,
**why a viewer would notice**, the fix in production terms, and a copy-ready **fix prompt** for an
image/video edit model (Nano Banana, GPT Image, Seedance etc.) that keeps everything else unchanged.

## 3. Hallucination checklist (always, every mode)

- **Hands**: count fingers on every visible hand, thumb on the correct side for left/right and palm/back view, knuckle and nail direction, fingers merging into objects or each other, grip that actually holds the object.
- **Anatomy**: limb count and length, joints bending the right way, feet and shoes (merged toes, two left feet), ears (shape, symmetry, earrings matching), teeth (count, blur into one strip), neck length.
- **Eyes**: pupils round and the same size, both looking at the same point, catchlights matching the light sources in the scene and matching between both eyes, glasses frames continuous and refracting.
- **Text and logos**: every sign, label, screen, licence plate, jersey, product label must be real readable text in the right language and spelling, or be deliberately unreadable through distance/focus. Gibberish glyphs are an instant FAIL.
- **Objects**: things merging (hair into collar, chair into leg, cup into hand), objects with no support, duplicated or cloned items (same person twice in a crowd, same tree repeated), broken repeats (fence posts, windows, tiles that change rhythm).
- **Architecture**: verticals and perspective consistent with one lens, windows and floors lining up, railings continuous, reflections in glass matching what is in front of it.
- **Animals**: leg count and gait, paw anatomy, fur direction, collar continuous.
- **Physics**: contact shadows where things touch the ground, cast shadows all pointing away from the same light, water/fabric/hair moving with gravity and wind, reflections in water, mirrors and sunglasses.

## 4. Realism tells (Photoreal everywhere, Hybrid on people and integration)

- **Skin**: pores, fine hair, uneven tone, redness around nose/eyes, real lip texture. FAIL on waxy, plastic, airbrushed, glossy "AI sheen", or the opposite: crunchy over-sharpened pores from an upscaler.
- **Light logic**: one consistent key direction per light source. If the sun is in frame, everything facing the camera is in its shade side and rimmed. Faces evenly front-lit while the sun is behind them = "two suns" = FAIL. Colour temperature of light on people matches the environment.
- **Lens and focus**: one focal plane; depth of field falls off smoothly with distance; no subject that is sharp while things at the same distance are soft; bokeh shape consistent; no cut-out edge sharpness (pasted look).
- **Texture and grain**: one noise/grain structure across the whole frame. Smooth-patch "watercolour" areas, halos around edges against the sky, HDR crunch and over-clarity on trees are upscaler tells.
- **Composition tells**: everything perfectly centred and perfectly symmetrical, everyone smiling at the same moment, too-clean environments with no litter, wear or randomness, generic stock-photo staging.
- **Colour**: saturation that no camera profile produces, teal/orange applied to everything, skin that does not respond to the environment colour.

## 5. Video-only checks

- **Identity lock**: the same face, hairline, moles, jewellery, outfit, logo on every frame. Compare first, middle, last frame and every cut.
- **Morphing**: fingers, teeth, text, patterns or background objects changing shape between frames; things appearing or disappearing without being occluded.
- **Motion**: weight and momentum (feet planting, no sliding), hair and cloth reacting to motion, camera move consistent with a real rig (no impossible floaty path unless drone), motion blur matching shutter (180° rule) and speed.
- **Temporal flicker**: texture boiling on skin, grass, water, brick; exposure pumping; lighting changing direction mid-shot.
- **Physics over time**: thrown objects follow an arc, liquids pour and settle, shadows move with their objects.
- **Edit**: shot-to-shot continuity (screen direction, prop positions, time of day), lip sync if there is dialogue.

## 6. Scoring

Score 0-100 on overall craft (light, lens, people, story, finish). It is shown for progress tracking only:
a 95 with one FAIL is still **FAIL**. Panel members each give 0-10 through their lens.
