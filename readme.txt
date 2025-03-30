# 16-bit Sprite Generator

A pixel art character sprite generator that creates animated 16-bit style game characters with various classes and animations.

---

## About This App

This application allows you to generate pixel art character sprites in different classes (Warrior, Archer, Mage) with multiple animation states (Idle, Walking, Attacking, Defending, Dying). Each sprite is procedurally generated with randomized colors and features while maintaining a cohesive 16-bit retro game aesthetic.

## Using The Sprite Generator

You can access the app in two ways:

### Option 1: Use the Pygame GUI Version
🎮 Run the desktop application for an interactive experience:

1. Install the required dependencies with `pip install -r requirements.txt`
2. Run the application with `python app.py`
3. Use the dropdown menus to select character class and animation type
4. Click "Generate Sprite" to create a new character
5. Adjust animation speed if desired
6. Use "Save Sprite" to export the animation frames as PNG files

### Option 2: Use the Web Version (If Configured)
🌐 Access through a web browser:

## Features

- Three character classes: Warrior, Archer, and Mage
- Five animation states: Idle, Walking, Attacking, Defending, Dying
- Randomized colors and appearances while maintaining class identity
- Variable animation speed settings
- Export animations as individual PNG frames
- Clean, intuitive interface

## Technical Details

- Built with Python and Pygame for the desktop application
- Optional Flask web interface
- Procedural sprite generation using pixel art techniques
- Animation handled through frame sequences
- 32x32 pixel sprites with transparency

### Animation Details

Dying: The sprite falls to the ground with a class-specific collapse

---

Feedback always welcome!

Email: Kameon@live.com

Created using Python, Pygame, and Flask. 2023.

Thank you,

-Kameon