# Saints Row Reboot Tools

Currently contains unpacking tool and experimental patch tool

## Extract
Input directory - Directory that contains desired `vpp_pc` and `str2_pc` files to extract

Output directory - Directory to extract the files too

Recursive - Whether to unpack the vcc_pc files and str2_pc files inside the files you are extracting

## Patch (Experimental)
Game directory - Directory that ends in `sr5`

Patch - will patch game files with data in `mod_data`, and update patched file information in `mod_config`

Open Mod Folder - will open `mod_data` in sr5 and create it if it doesn't exist

Unpatch - will read data in `mod_config` and remove all applied patches

# Build
To Build exe for Windows:
```
pip3 install -r requirements.txt
pyinstaller gui.py
```