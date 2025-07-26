# Usage
1. Generate a .csv file containing data for DnD 5e magic items or spells.
    1. Look up the items/spells in the https://5e.tools/items.html search
    2. Add/pin those to the sidebar list
    3. Click "Table View" and then download the CSV for all of the pinned list items
3. Run src/convert.py <csv file path> <html output path> (<Class / Source name for cards>)
4. Clone my Homebrewery DnD cards [template file](https://homebrewery.naturalcrit.com/share/CL92fQjuQvxi)
5. Copy-paste the generated HTML file into the Homebrewery template
6. You may want to edit the cards so that they're more readable.
    1. Item and spell cards both have color settings in their HTML block- you may want to tweak these. (There are some class-specific colors defined in the template's CSS file.)
    2. The script is not perfect at resizing text to fit; you may need to tweak the font size in the cards' HTML block so that longer card texts fit.
    3. Also, consider editing the actual text of the card for readability!
