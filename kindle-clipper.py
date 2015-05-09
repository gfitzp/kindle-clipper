#!/usr/bin/env python3

# The MIT License (MIT)
# 
# Copyright © 2015 Glenn Fitzpatrick
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os, re, sys


# when using as an embedded script in Hazel, the matched file name is passed to this script as the first argument
# open the file as read-only
# kindle clipping text files are UTF-8 encoding with BOM, so we use the utf-8-sig encoding

clippings = open(sys.argv[1], 'r', encoding='utf-8-sig')


# read in all of the lines in the file
lines = iter(clippings.readlines())


# the lines in the file look something like this:
# 
# Casino Royale (James Bond) (Ian Fleming)
# - Highlight on Page 43 | Loc. 596-97  | Added on Friday, October 11, 2013, 12:08 PM
# 
# ‘My name’s Felix Leiter,’ said the American. ‘Glad to meet you.’ ‘Mine’s Bond – James Bond.’ 
# ==========
# 
#
# that is, a file with multiple clippings would look like...
#
# Title (Author)
# - Highlight on Page 1 | Loc. 1-999 | Added on Day, Month, Date, Year, Hour:Minute Time
#
# Body of clipping.
# ==========
# Title (Author)
# - Highlight on Page 1 | Loc. 1-999 | Added on Day, Month, Date, Year, Hour:Minute Time
#
# Body of clipping.
# ==========
# Title (Author)
# - Highlight on Page 1 | Loc. 1-999 | Added on Day, Month, Date, Year, Hour:Minute Time
#
# Body of clipping.
# ==========
#
# we want to extract each of those individual clippings to their own separate files, organized by item title.
# we don't need to know the day the clipping was made. the goal is to have each of those individual clippings as a file
# that looks like:
#
# Title: title
# Author: author
# Page 1 | Loc. 1-999
#
# Body of clipping.


# start with the first line in the clipped section
# we use clippingline as a counter to determine what to do depending on where we are in the clipped section
clippingline = 0

# set the body of the first clipping to an empty string
clippingbody = ''


# for each line that was read in
for line in lines:
    
    if "- Your Note on " in line:
        next(lines)
        next(lines)
        next(lines)
        clippingline = 0
        clippingbody = ''
        continue

    # if it's the first line in the clipped section
    if clippingline == 0:
        
        # the first line in the clipped section has the title of the item the clipping came from
        # and also has the author of that item. we need to do some regex on that first line to extract
        # the title of the item and the item's author:
        #
        # Casino Royale (James Bond) (Ian Fleming)
        
        
        # get the clipping title
        # sometimes the title has a parenthetical section, like in this example
        # we want everything up until the space between the title and the last parenthetical section
        # on this line, which contains the author's name
        
        regex_title = re.compile(r"(?P<title>.*)\s(?=\(.*\)$)")
        result = regex_title.search(line)
        clippingtitle = result.group('title')


        # get the clipping author
        # the item's author is in the last parenthetical section on the line, so we grab everything inside
        # that last parenthetical section as the author's name
        
        regex_author = re.compile(r"\((?P<author>[^)]*)\)$(?!.*\()")
        result = regex_author.search(line)
        clippingauthor = result.group('author')


        # move to the next line in the clipping section
        clippingline = clippingline + 1



    elif clippingline == 1:
    
        # the second line in the clipped section has the location of the clipping and the date it was clipped:
        #
        # - Highlight on Page 43 | Loc. 596-97  | Added on Friday, October 11, 2013, 12:08 PM
        #
        # the page number is optional, only items with real page numbers contain that field. if this item did not
        # have real page numbers, it would look like this:
        #
        # - Highlight Loc. 596-97  | Added on Friday, October 11, 2013, 12:08 PM
        #
        # here we grab the page number (if it exists) and the location so we can reference it in our output. we'll
        # also extract the actual location numbers so we can use that as part of the output file's filename.
    
    
        # get the clipping location
        
        regex_location = re.compile(r"\- Your (Highlight|Note) on (?P<location>(page.*)?.*Location\s(?P<loc>\S*))")
        result = regex_location.search(line)
        clippinglocation = result.group('location') # Page 43 | Loc. 596-97
        clippinglocation = clippinglocation.replace('page', 'Page')
        loc = result.group('loc') # 596-97


        # move to the next line in the clipping section
        clippingline = clippingline + 1


    
    elif clippingline == 2:
        
        # the third line in the clipped section is a blank line between the details of the clipping and the body of
        # the clipped section. we just skip to the next line to start clipping the body of the clipping.
        
        clippingline = clippingline + 1



    elif clippingline == 3 and line != '==========\n':
        
        # the fourth line starts the actual body of the clipping. most clippings i've found have saved the body as a
        # single line, but one i've found (i'm looking at you, Feynman's Rainbow: A Search for Beauty in Physics and in Life)
        # had carriage returns in the middle of the body. since the body of the clipping goes until there is a '==========\n'
        # line, we just keep reading in lines and appending them to the lines we've already read so far until we reach
        # that '==========\n' line. if there do happen to be multiple lines split by carriage returns in the middle of the
        # body, we join those lines together with line feeds to make the output a little nicer to read.
        #
        # ‘My name’s Felix Leiter,’ said the American. ‘Glad to meet you.’ ‘Mine’s Bond – James Bond.’ 
    
        # get the whole line as the clipping body and join it to any previous lines in the body
        clippingbody = '\n'.join([clippingbody, line])


    
    elif line == '==========\n':
        
        # once we reach the '==========\n' line that's the end of the clipped section so now we can create the output file
    
    	# if the book's (clipping's) directory doesn't yet exist, create it
    	# if there's a ':' in the book's title, replace it with a '-' for the filesystem
    	
        if not os.path.exists(clippingtitle.replace(':', '-')):
    	    os.makedirs(clippingtitle.replace(':', '-'))

        # change to the book's directory
        os.chdir(clippingtitle.replace(':', '-'))
    	
    	
        # create the clipping file
        # name the clipping file as the clipped item's title and the location of the clipping:
        #
        # Casino Royale (James Bond) 596-97.txt
        
        filename = " ".join([clippingtitle.replace(':', '-'), loc])
        filename = filename + ".txt"
        output = open(filename, 'w', encoding='utf-8')


        # write to the clipping file. the output will look like:
        #
        # Title: Casino Royale (James Bond)
        # Author: Ian Fleming
        # Page 43 | Loc. 596-97
        # 
        # ‘My name’s Felix Leiter,’ said the American. ‘Glad to meet you.’ ‘Mine’s Bond – James Bond.’
        
        output.write("".join(["Title: ", clippingtitle.strip(), '\n']))
        output.write("".join(["Author: ", clippingauthor.strip(), '\n']))
        output.write("".join([clippinglocation.strip(), '\n\n']))
        output.write(clippingbody.strip())


        # close the output file
        output.close()
        
        
        # go back to the top-level directory
        os.chdir('..')
        
        
        # start anew on the next block of clipping text
        clippingline = 0
        clippingbody = ''


# close the My Clippings.txt file
clippings.close()
