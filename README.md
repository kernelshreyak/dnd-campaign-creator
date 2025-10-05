# DnD 5e Campaign Creator

A PyQt-based GUI application for creating and managing Dungeons & Dragons 5e campaigns, inspired by Fantasy Grounds and 5etools. Easily create, edit, and organize characters, spells, items, NPCs, and campaign notes, all saved in a user-chosen campaign folder.

## Features

- **Campaign Management**: Create or load campaigns, each stored in its own folder.
- **Character Creation**: Paste 5etools stat blocks and (AI-assisted) parse them into structured character sheets.
- **Spell Management**: Add and edit spells with all key fields.
- **Item/Weapon Management**: Add and edit weapons, armor, gear, magic items, and more.
- **NPC Management**: Create and categorize NPCs as hostile, friendly, or neutral.
- **Campaign Notes**: Write and render campaign notes in Markdown, with live preview.
- **Data Storage**: All campaign data is saved as JSON/Markdown files in the selected campaign folder for easy backup and sharing.

## Installation

1. **Install Python 3.7+** (https://www.python.org/downloads/)
2. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. **Run the app**:
   ```
   python main.py
   ```
2. **Create or Load a Campaign**:
   - Click the "Create/Load Campaign" button in the Campaign tab.
   - Enter a campaign name and choose a folder, or load an existing campaign folder.

3. **Manage Campaign Content**:
   - **Characters**: Paste a 5etools stat block and click "Parse Stat Block" to auto-fill fields (AI parsing placeholder).
   - **Spells/Items/NPCs**: Use the respective tabs to add and edit entries.
   - **Notes**: Write campaign notes in Markdown and render them for preview.

4. **Saving and Loading**:
   - All data is automatically saved in the campaign folder as you add content.
   - To load a campaign, use the "Load" option in the Campaign tab and select the campaign folder.

## Project Structure

See [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) for a detailed breakdown of the codebase.

## Requirements

- Python 3.7+
- PyQt5
- markdown

## Notes

- Stat block parsing is a placeholder; for advanced parsing, integrate an AI/NLP backend.
- All campaign data is stored locally in the folder you choose.
- This app is not affiliated with Wizards of the Coast, Fantasy Grounds, or 5etools.

## License

MIT License