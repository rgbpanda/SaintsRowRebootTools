# Saints Row Reboot Tools

Currently contains unpacking tool. More details/updates to come in the future

## Recursive File Extracter
Input directory - Directory that contains desired `vpp_pc` and `str2_pc` files to extract

Output directory - Directory to extract the files too

Recursive - Whether to unpack the vcc_pc files and str2_pc files inside the files you are extracting

# Build
To Build exe for Windows:
```
pip3 install -r requirements.txt
pyinstaller gui.py
```