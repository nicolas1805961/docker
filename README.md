# Simple page detection and dewarping tool
(c) 2016 - Joseph Chazalon

This tools enables to detect and dewarp (correct the perspective transform)
from a camera-captured document image.

Given a picture of a document page captured with a smartphone, the tool
returns the coordinates of the corners of the page outline.

Constraints:
- the document must be in A4 format
- the document must be oriented in portrait (long edge mostly vertical)
- the contrast with the background must be clear

# Simplifications for the DVIRT course
- no dewarping (just return the coordinates of the corners of the page outline)
- no image output (remplaced by JSON)
- no GUI

The full version returns a "flat" image of the document page, like if it was
captured with a flatbed scanner.

# Installation
Just copy the `dewarp.py` file and make sure you have the following modules
available in your PYTHONPATH:
- numpy
- opencv

# Sample usage
~~~~
python dewarp.py input_samples/sample01.png /tmp/page_coords_output.json
~~~~
