# AbsolutLEE · Bangkok headshots (Rochelle) · draft storyboard

Standalone video, not part of the abroad series. AbsolutLEE look: Bootzy callouts (butter yellow and white), eye-level karaoke captions without punctuation, iOS emoji pairs, light film look, sound effects only on events.

Reference: Holo Face reel. Big bold words in mixed sizes, some words behind the person, a cut about every second.

## Voiceover script (Rochelle, final edits)

> POV: this is your sign to update your LinkedIn photo while you're on holiday.
>
> If you're in Bangkok, book a headshot at Holo Face. Here's exactly how it works.
>
> You check in, and a stylist asks what you're going for: soft or bold makeup, your outfit, even your backdrop, so it all comes together.
>
> Then it's an hour of hair and makeup, while you pick from a huge wardrobe of styles and outfits. Basically, playing dress-up as an adult, but make it professional.
>
> Before you lock in your look, you do test shots on camera. I started in pants, but it wasn't flattering, so I decided to change into a skirt.
>
> And if you're awkward in front of the camera like me, they literally teach you how to pose. Chin down, shoulders back, and somehow I look like I know what I'm doing.
>
> After about fifteen minutes of shooting, you pick your photos. The hardest part. I booked one… and walked out with three. Self-control was not part of the package.
>
> The edits came back the same day. In their app, you see the before and after, and message the editor exactly what to change.
>
> The next day we picked up our prints, and I gave Josh my photo card. Because I'm the only idol he has, obviously.
>
> New LinkedIn photo, unlocked. Would you do this on your next holiday?

Facts: Holo Face, Emsphere mall. Booked 1 photo, upgraded to the 8th-anniversary 3-photo package, THB 3,888 total.

## Beats

| # | Footage | Big text and effects |
|---|---|---|
| 1 | Final photo IMG_8002 with a flash, then quick cuts: makeup, studio, monitor | POV hook in Bootzy: "**POV:** your sign to update your **LINKEDIN** photo on **holiday**" 💼📸 |
| 2 | Holo Face exterior (7669, 7600/7601), walking in (7670) | **HOLO FACE** 📍✨ |
| 3 | iPad menu (7668), stylist chat, wardrobe (7608, 7665, 7666, 7626) | "**SOFT** or **BOLD**?" 💄🎨 |
| 4 | Hair and makeup: Rochelle (7616, 7617, 7621, 7622), friend (7613, 7618, 7623) | **1 HOUR** glam 💇‍♀️💄 |
| 5 | Wardrobe and friend picking her outfit (7612 "going for the full white look"), shoes and accessories (7628, 7627), fitting-room selfies (7609, 7610, 7625) | "**SO MANY** styles" 👗👠. The friend appears here as the "different styles" example. |
| 6 | Pants test shot (7625) then the skirt look (7634) | **TEST SHOTS** behind Rochelle (text-behind-person). "pants ❌ skirt ✅" |
| 7 | Posing on grey (7634, 7636), friend on white with the photographer directing (7658–7661, 7663) | **POSE** behind the subject. "awkward like me" 🙈📸 |
| 8 | Monitor review (7635), the photo-picking wall (camphoto), choosing (7664) | "**ONE** → **THREE**" 😩➡️😍 |
| 9 | App before/after screens (7996–7998) | **SAME DAY** edits ⚡📱 |
| 10 | Reveal: the 3 final photos (8001–8003), each with a flash, shutter sound and zoom | ✨😍 |
| 11 | Joshua with the photo card in his phone case (8395, 8396) | 🥹💛 |
| 12 | End card: LinkedIn "I'm happy to share…" post (`endcard_mock.jpg`) with details and reactions | **NEW PFP UNLOCKED** 🔓💼 |

## Applied with Rochelle's voiceover (done)

1. **Hook text:** "pov: this is your sign to update your" goes on **two lines**, all **lowercase** at the smaller size (line 1 "pov: this is your sign to", line 2 "update your"). Then **LINKEDIN PHOTO** (big, white) and "while you're on holiday" as now.
2. **TikTok safe area for everything** (text, emojis, callouts, tags, badges, LinkedIn card):
   - TikTok crops the sides on tall phones (about 100px each side of a 1080px-wide frame).
   - The top has the search bar, the right edge has the like/comment/share buttons, and the bottom has the username, caption and progress bar.
   - Keep all elements inside roughly x 110–940 and y 190–1480 (1080×1920 units), and scale down anything wider.
   - Apply this as a global clamp in the editor so future videos follow it automatically.
3. **Photo cards (~1:13):** IMG_8395 now starts at 5.3s, with Josh already reaching for a card instead of staring at the backs (done in render.py).

**Voiceover clean-up:**
- Kept the second "test shots" take, which includes "on camera".
- Dropped the "picked up our edits… sorry" fumble.
- Kept her ad-libs: "or even Sims", "and once you're locked in, you start", "three rounds of edits".
- Ran the clean-up with `--keep 0:35.5 --keep 39.3:82.6 --keep 88.3:999`.
