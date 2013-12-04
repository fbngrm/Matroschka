om PIL import Image
from math import sqrt
import errno
import glob
import os
import readline
import sys

def complete(text_file, state):# Used for AutoComplete for Files
    return (glob.glob(text_file+'*')+[None])[state]

def decrypt_image(image_file, text_file):#Turns a Image in a file 
    if not os.path.exists(image_file): raise IOError('File does not exist: %s' % image_file)
    img = Image.open(image_file)
    with open(text_file, 'w') as txt:
        txt.write(img.tostring())

def encrypt_image(image_file, text_file):#Turns a File in to a Image file Does not  have to be a text file
    if not os.path.exists(text_file): raise IOError('File does not exist: %s' % text_file)
    srctext = open(text_file).read()
    size = int(sqrt(len(srctext)))
    Image.fromstring('L', (size,size), srctext).save(image_file)

# Used to set up the AutoComplete 
readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)

# using global varables because I had some problems with local varables
global encrypt 
encrypt = ''
global image 
image = ''
global text 
text = ''


if len(sys.argv)!=5 and len(sys.argv)!=1: # if a argument was given but not the correct ones
    print "Use: ./%s -i [Input File] -o [Output File]" % sys.argv[0]
else:# still working on makeing this better because if it has 4 args but no -o -i or both it raises an error
    if len(sys.argv)==1:
        encrypt = 'd' if raw_input("Encrypt or decrypt a file (E/d):") in ('d', 'D') else 'e'
        image = (lambda default, input: default if input.strip() == '' else input)("a.png", raw_input("Image File name(a.png):"))
        text = (lambda default, input: default if input.strip() == '' else input)("a.out", raw_input("Text File name(a.out):"))
    else:
        for num, args in enumerate(sys.argv):
            if args == '-o':
                if sys.argv[num+1][-4:].lower().strip() in ('.png', '.jpg', 'jpeg', 'gif'):
                    encrypt = 'e'
                    image = sys.argv[num+1].strip()
                else:
                    encrypt='d'
                    text = sys.argv[num+1].strip()
            elif args == '-i':
                if sys.argv[num+1][-4:].lower().strip() in ('.png', '.jpg', 'jpeg', 'gif'):
                    encrypt = 'd'
                    image = sys.argv[num+1].strip()
                else:
                    encrypt = 'e'
                    text = sys.argv[num+1].strip()
                    
    if encrypt=='d':
        decrypt_image(image, text)
    else:
        encrypt_image(image, text)