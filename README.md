# SpaCy NER Fine-tuning Tool

This is a PyQt5 application for fine-tuning the Named Entity Recognition (NER) component of a SpaCy model. The tool allows users to manually tag entities in text and save the annotations in JSON format. It supports bulk tagging and includes features for undoing and redoing annotations.

## Features

- **Load Text Files**: Open and display text files for annotation.
- **Manual Tagging**: Select text and tag it with a specified entity type.
- **Bulk Tagging**: Automatically tag all occurrences of a specified text with a given entity type.
- **Undo/Redo**: Undo and redo tagging actions.
- **Save Annotations**: Save the tagged entities in JSON format.
- **Context Menu**: Right-click on tagged entities to delete them.
- **Status Bar**: Display messages in the status bar.
- **Credits**: Link to the developer's GitHub profile.

## Prerequisites

- Python 3.x
- SpaCy
- PyQt5

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/MaddyDev-Glitch/ner-finetuning-tool.git
    cd ner-finetuning-tool
    ```

2. **Create a virtual environment and activate it**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the dependencies**:

    ```bash
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    ```

## Usage

1. **Run the application**:

    ```bash
    python main.py
    ```

2. **Load a text file**:
    - Click on the `Open File` button and select a text file to load.

3. **Manual Tagging**:
    - Select text in the main window.
    - Enter the tag name in the `Enter tag here...` box and press `Enter`.

4. **Bulk Tagging**:
    - Enter the text to be tagged in the `Enter text to tag...` box.
    - Enter the tag name in the `Enter tag for bulk text...` box.
    - Click on the `Apply Bulk Tag` button.

5. **Undo/Redo**:
    - Use `Ctrl+Z` to undo the last action.
    - Use `Ctrl+Y` to redo the last undone action.

6. **Save Annotations**:
    - Click on the `Save to JSON` button and choose the location to save the JSON file.

7. **Delete Tagged Entities**:
    - Right-click on an entry in the list and select `Delete` to remove the tag.

## Credits

Developed by [MaddyDev-Glitch ✨](https://github.com/MaddyDev-Glitch)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

### Sample Screenshot

![Sample Screenshot](screenshot.png)

---
