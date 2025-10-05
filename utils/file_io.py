import os
import json

def save_entity(entity_type, data, campaign_folder):
    """Save a single entity (character, spell, item, npc, notes) as JSON in the campaign folder."""
    os.makedirs(campaign_folder, exist_ok=True)
    file_path = os.path.join(campaign_folder, f"{entity_type}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    else:
        all_data = []
    all_data.append(data)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)

def load_entities(entity_type, campaign_folder):
    """Load all entities of a type from the campaign folder."""
    file_path = os.path.join(campaign_folder, f"{entity_type}.json")
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_notes(notes_text, campaign_folder):
    """Save campaign notes as markdown text."""
    os.makedirs(campaign_folder, exist_ok=True)
    file_path = os.path.join(campaign_folder, "notes.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(notes_text)

def load_notes(campaign_folder):
    """Load campaign notes as markdown text."""
    file_path = os.path.join(campaign_folder, "notes.md")
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()