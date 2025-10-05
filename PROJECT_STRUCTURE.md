# DnD 5e Campaign Creator - Project Structure

## Directory Layout

```
dnd_campaign_creator/
│
├── main.py                  # Entry point, launches the PyQt app
├── gui/
│   ├── main_window.py       # Main window and navigation
│   ├── campaign_dialog.py   # Campaign creation/loading dialog
│   ├── character_editor.py  # Character creation/editing UI
│   ├── spell_editor.py      # Spell creation/editing UI
│   ├── item_editor.py       # Weapon/Item creation/editing UI
│   ├── npc_editor.py        # NPC creation/editing UI
│   └── notes_editor.py      # Markdown notes editor/viewer
│
├── models/
│   ├── campaign.py          # Campaign data structure
│   ├── character.py         # Character data structure & stat block parser
│   ├── spell.py             # Spell data structure
│   ├── item.py              # Weapon/Item data structure
│   └── npc.py               # NPC data structure
│
├── utils/
│   ├── file_io.py           # Save/load logic for campaign data
│   └── markdown_viewer.py   # Markdown rendering helper
│
├── requirements.txt
└── README.md
```

## Main Modules

- **main.py**: Starts the application, sets up the main window.
- **gui/main_window.py**: Central navigation (tabs or sidebar) for Characters, Spells, Items, NPCs, Notes, Campaign management.
- **gui/campaign_dialog.py**: Dialog for creating/loading campaigns, choosing folder/name.
- **gui/character_editor.py**: UI for character creation, stat block input, AI-assisted parsing.
- **gui/spell_editor.py**: UI for spell creation/editing.
- **gui/item_editor.py**: UI for weapon/item creation/editing.
- **gui/npc_editor.py**: UI for NPC creation/editing (hostile, friendly, neutral).
- **gui/notes_editor.py**: Markdown editor and viewer for campaign notes.
- **models/**: Data classes for campaign, character, spell, item, NPC.
- **utils/file_io.py**: Handles saving/loading all campaign data to/from the selected folder.
- **utils/markdown_viewer.py**: Renders markdown to HTML for display in the GUI.

## Data Storage

- Each campaign is a folder named by the campaign name, chosen by the user.
- All campaign data (characters, spells, items, NPCs, notes) is saved as JSON or similar files in the campaign folder.

## Next Steps

- Implement the PyQt GUI skeleton and navigation.
- Implement campaign creation/loading.
- Implement editors for characters, spells, items, NPCs, and notes.
- Implement save/load logic.
- Add requirements.txt and README.md.