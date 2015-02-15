### How to compile with py2exe (32-bit version necessary)

1. Move SilentMapConverter.py into this directory.
2. Run setup.py
3. The new .exe file will be in the dist directory

### Creating the .ico file

1. I use the excellent [PHP ICO Generator](https://github.com/chrisbliss18/php-ico) (Thanks for taking the time to actually figure out the .ico format)
2. Array of sizes supplied to generator must go from largest to lowest for py2exe