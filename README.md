# Snakes & Ladders — PyGame

## Installation
- Create a virtual environment in PyCharm (Python 3.10+).
- Install dependencies: `pip install -r requirements.txt`.
- Mark `src/` as Sources Root.

## Run Configurations
- Development: run `src/main.py` with `GAME_MODE=dev` or `--debug`.
- Production: run `src/main.py` with `GAME_MODE=prod` or `--no-debug`.
- Tests: run `pytest` in the `tests/` folder.

## Controls
- Roll: click Roll or press space.
- Pause: click Pause.
- Save: click Save.
- Restart: click Restart.
- Menu: click Menu.

## Known Issues
- Visual assets fall back to programmatic rendering when files are missing.
- On HiDPI displays scaling may require system settings adjustment.

## Future Enhancements
- Networked multiplayer and AI opponents.
- Themed boards and alternate modes.
- Mobile build and localization.