# kindle-clipper
Python 3 script to extract clippings from My Clippings.txt file on Kindle and save each as its own file.


## Usage

Add the `Kindle Clippings.hazelrules` document as a set of rules to a folder in [Hazel](http://www.noodlesoft.com/hazel.php). 

When Hazel encounters a file named `My Clippings` in the watched directory it will pass that file as an argument to the script. The script itself will extract each individual clipping from the file and save each as its own file, named with the book title and Kindle locations of the clipped text, and grouped into directories by book title. Once all clippings have been extracted Hazel will delete the `My Clippings.txt` file.

The `kindle-clipper.py` Python script is the same script for using outside of Hazel. Pass the `My Clippings.txt` file as the first argument to the script for processing.