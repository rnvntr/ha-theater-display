# Home Assistant dashboard setup

The Pi runs the browser. Home Assistant serves the dashboard and poster images.
`deploy.sh` installs the Pi side only. Complete this HA setup once, then use the
dashboard URL when deploying any display Pi. No access token belongs in this repo.

## 1. Install the card and media integrations

Install **Button Card** (`custom-cards/button-card`, version 7 or newer) through
HACS, or follow its [manual installation instructions](https://custom-cards.github.io/button-card/stable/).
Ensure its JavaScript module is registered in HA dashboard resources, then reload
the browser. HACS normally registers `/hacsfiles/button-card/button-card.js`.
The template needs no custom theme, active-player helper, time sensor, or automation.

Set up your Plex, Cast, TV and/or music integration in HA. In Developer Tools →
States, find each theater player's entity ID and confirm it reports `playing`,
`buffering`, `paused` and media attributes when used. Configure only players in
the theater: this dashboard intentionally does not search every room.

## 2. Import and configure

Create a new empty dashboard in Settings → Dashboards with URL path
`theater-display`. Open it, enter edit mode and open the raw configuration editor.
Replace that new dashboard's configuration with
[`home-assistant/dashboard.yaml`](../home-assistant/dashboard.yaml).
This is a **complete dashboard** containing one panel view, not a card snippet.
Keep a backup before replacing any existing dashboard.

Edit only the `variables` block near the top:

```yaml
variables:
  players:
    - media_player.theater_plex
    - media_player.theater_cast
  weather_entity: weather.home
  poster_files:
    - example-poster.jpg
    - another-poster.webp
  rotation_seconds: 120
```

Replace the example entity IDs with your own. List the highest-priority player
first; remove unused entries. Set `weather_entity: ''` to omit weather data.
Missing weather data displays a dash. The card uses current weather attributes;
high/low values appear only if the integration exposes a forecast attribute.
It does not call the weather forecast service.

## 3. Add idle posters

On the **HA server**, create `www/theater-posters` beside `configuration.yaml`
(usually `/config/www/theater-posters`). Upload your own JPG, PNG or WebP images
there using your existing HA file editor or file sharing access. If you created
`www` for the first time, restart HA. Verify each image opens at:

```text
https://HA_HOST/local/theater-posters/example-poster.jpg
```

Add the exact filenames, including case and extensions, to `poster_files`.
Keep an empty list (`[]`) for the gradient lobby without idle images. Images are
not bundled, downloaded, or copied by the Pi installer. Now-playing artwork comes
from the selected media player's attributes, so it depends on that integration.
Poster files are static HA content and [are accessible without HA authentication](https://www.home-assistant.io/integrations/http/#hosting-files);
only put images you intend to serve there. Never place configuration or tokens in `www`.

## 4. What triggers changes?

The card's `update_timer: 10000` redraws every ten seconds while the view is open.
This also advances the clock and idle poster rotation without `sensor.time`.
There are no server-side automation triggers to install.

| Condition at refresh | Display |
| --- | --- |
| One or more configured players playing/buffering | First matching player in `players` |
| No player playing/buffering, but one paused | First paused player |
| All configured players idle/off/unavailable/missing | Idle lobby |
| Idle rotation interval passes | Next filename in `poster_files`, looping |

Playback changes may take up to ten seconds to appear. Rotation uses wall-clock
time, so reloading does not always start with the first image. Paused content stays
visible until its player changes state. A TV reporting only `on` does not count as
playback; use its Cast/Plex entity if it provides richer playback state.

The template retains the supplied poster presentation, title/provider metadata,
music handling and lobby layout. Personal entity IDs, hardcoded movie filenames,
the theme dependency and home-specific tornado shelter overlay were removed.
Weather alerts require a separate, locally configured alert system; this template
does not install one or redirect people to a particular room.

## 5. Connect and check the Pi

Open `/theater-display/streaming` in HA and verify playback, pause and idle states.
Then run `sudo bash deploy.sh` on the Pi and enter that full dashboard URL.
Sign in once with a dedicated display account. Chromium fullscreen hides browser
chrome; it does not hide HA's own header/sidebar. HA kiosk styling is optional and
not a required dependency of this template.

Check on the actual TV: rotation, text fit, idle artwork, two-minute poster change,
player priority, missing artwork, pause, stop, and persistence after reboot.
The repository tests cover rendering logic; they do not prove the actual HA frontend
or physical display works. If you see “Custom element doesn't exist: button-card”,
check the module resource and refresh. For missing posters, open their `/local/`
URLs directly. For stale playback, inspect the player's state in Developer Tools.

See [HA dashboard documentation](https://www.home-assistant.io/dashboards/dashboards/)
and [button-card refresh options](https://custom-cards.github.io/button-card/stable/config/main/).
