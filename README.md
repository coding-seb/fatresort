# fatresort

GUI for managing the order of .mp3 files on a FAT filesystem like a USB stick. 
This is helpful for car stereos that play files in alphabetical order.

Currently only supports alphabetical ordering and no custom order.

Note that the software only moves files from the selected directory to a temporary directory and back in the desired order.
This process might take a while and needs enough free disk space.

To install dependencies (currently only PyQt6):
```bash
pip install -r requirements.txt
```

To run the application:
```bash
python src/fatresort/gui.py
```
