# GfxAoVivo widgets

The widgets listed under **Discover widgets** in [GfxAoVivo](https://github.com/alfredriesen/gfx-ao-vivo). The app reads [`registry.json`](registry.json) from `main` (`https://raw.githubusercontent.com/alfredriesen/gfx-ao-vivo-widgets/main/registry.json`), so a widget shows up in every app once its pull request is merged.

```
registry.json                 the list
widgets/<name>-<version>.zip  the plugin ZIPs
previews/<name>.png           one preview image per widget (640×360 works well)
pack.sh                       zips a widget folder and prints its version, zip and sha256
scripts/check.py              the check CI runs on every pull request
```

## Adding or updating a widget

1. Write the widget as an ordinary GfxAoVivo plugin; see [Writing a plugin](https://github.com/alfredriesen/gfx-ao-vivo#writing-a-plugin). The included widgets' sources live in the app repo's [`widgets/`](https://github.com/alfredriesen/gfx-ao-vivo/tree/main/widgets) folder.
2. When you change a widget that is already listed, bump `version` in its `manifest.json`. The app offers an update whenever the registry's version is higher than the installed one.
3. Run `./pack.sh path/to/widget`. It writes `widgets/<name>-<version>.zip` and prints the `version`, `zip` and `sha256` lines for the entry. Delete the old ZIP when you replace one.
4. Add a preview image to `previews/`: a 16:9 screenshot of the graphic on air.
5. Add or update the entry in `registry.json`, run `python3 scripts/check.py`, and open a pull request.

```json
{
  "name": "lower-third",
  "displayName": "Lower Third",
  "description": "A name and title banner that wipes in from the left.",
  "category": "talk",
  "version": "1.0.0",
  "preview": "previews/lower-third.png",
  "zip": "widgets/lower-third-1.0.0.zip",
  "sha256": "…",
  "author": "Your name",
  "official": false
}
```

| Field | Meaning |
| --- | --- |
| `name` | The plugin's `name` from its manifest. The app refuses a ZIP whose manifest has another name or version than the entry |
| `displayName`, `description` | Shown on the gallery card |
| `category` | One of `talk`, `sports`, `news`, `church`, `gaming`, `general` (others show up as their own category) |
| `version` | The manifest's `version` |
| `preview` | Image shown on the card; a path in this repo or an `https://` URL |
| `zip` | The plugin ZIP; a path in this repo or an `https://` URL |
| `sha256` | SHA-256 of the ZIP. The app installs nothing whose hash differs |
| `author` | Who made it |
| `official` | `true` only for widgets maintained by the GfxAoVivo project; shows the **Official** badge |

## Reviewing a submission

CI checks that every entry is complete, that each ZIP has the listed hash, name and version, and that each preview exists. Widgets run in GfxAoVivo's [sandbox](https://github.com/alfredriesen/gfx-ao-vivo#sandbox), so they can't reach the network or the rest of the app. Still read the code before merging: check that it only does what the description says and that it sets user text with `textContent`.

Don't have a widget but an idea for one? [Suggest it](https://github.com/alfredriesen/gfx-ao-vivo/issues/new?template=widget-idea.yml).
