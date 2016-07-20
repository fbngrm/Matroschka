# -*- coding: utf-8 -*-

try:
    import Image
except:
    from PIL import Image

import itertools


def as_32_bit_string(n):
    """return param n(must be an int or char) packed in a 32 bit string"""
    # rightshift n bytewise from 0 to 3 bytes. use chr(n) to chop 1 byte
    # representation of the current shifting position
    byte_string = ''
    for c in range(24, -8, -8):
        byte_string += chr(n >> c & 0xff)
    # return n packed in a 32 bit string
    return byte_string


def as_bits(data):
    """
    returns a generator that provides a bit representation
    of the input data
    """
    # bit representation of the payload
    # itertools.product: cartesian product of input iterables
    # product(A, B) returns the same as ((x,y) for x in A for y in B)

    # all chars in data will be shifted 7,6,5,4,3,2,1,0 bits to the right
    # thus a binary/bit representation of char is created
    return (ord(char) >> shift & 1
            for char, shift in itertools.product(data, range(7, -1, -1)))


def n_tupled(data, n, fillvalue):
    """
    returns an iterator that packs data in tuples of length n
    padded with the fillvalue
    """
    # izip_longest(*iterables[, fillvalue])
    # izip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
    # make an iterator that aggregates elements from each of the iterables.
    # if the iterables are of uneven length, missing values are filled-in with
    # fillvalue. iteration continues until the longest iterable is exhausted.

    # cast data to an iterator and pass it n times in a tuple to izip_longest
    # the generator exhaustes itself while zipping - thats why passing
    # *[iterator]*n works
    return itertools.izip_longest(*[iter(data)] * n, fillvalue=fillvalue)


def hide_msg(image, data):
    """"
    hide the payload in the least significant bits of the image
    return the manipulated image or None
    """

    def set_least_sig_bit(cc, bit):
        """
        set the least significant bit of a color component
        """
        # get the lsb by a bitwise and of the color component and
        # the inversion of 1
        # manipulate the lsb by a bitwise or with the bit to set
        return cc & ~1 | bit

    def hide_bits(pixel, bits):
        """
        hide the bit in a color component
        return the tupled pixel with manipulated lsb
        """
        # tuple the 3 color components and the 3 payload bits by
        # passing them to the zip function. zip returns a list of tuples
        # instead of an iterator(like izip)
        return tuple(itertools.starmap(set_least_sig_bit, zip(pixel, bits)))

    hdr = as_32_bit_string(len(data))
    payload = '%s%s' % (hdr, data)
    n_pxls = image.size[0]*image.size[1]
    n_bnds = len(image.getbands())

    if len(payload)*8 <= n_pxls*n_bnds:
        img_data = image.getdata()
        # create a generator(with tuples of length n_bnds) that
        # iterates over every bit of the payload
        payload_bits = n_tupled(as_bits(payload), n_bnds, 0)
        # starmap - makes an iterator that calls the hide_bits function using
        # arguments obtained from the zipped image data and payload
        # (tupled by izip)
        new_img_data = itertools.starmap(
            hide_bits, itertools.izip(img_data, payload_bits))
        # create the image with the manipulated least significant bits
        image.putdata(list(new_img_data))
        return image


def extract_msg(image):

    def get_least_sig_bits(image):
        """get the least significant bits from image"""
        pxls = image.getdata()
        return (cc & 1 for pxl in pxls for cc in pxl)

    bits = get_least_sig_bits(image)

    def left_shift(n):
        # reduce(function, iterable[, initializer])
        # reduce(lambda x,y: x+y, [1, 2, 3, 4, 5]) calculates ((((1+2)+3)+4)+5)
        # apply function of two arguments cumulatively to the items of iterable
        # from left to right, so as to reduce the iterable to a single value.

        # create a an iterator of the first n bits
        n_bits = itertools.islice(bits, n)
        # bitwise or n bits to get an int
        return reduce(lambda x, y: x << 1 | y, n_bits, 0)

    def next_ch():
        return chr(left_shift(8))

    def defer(func):
        return func()

    n_pxls = image.size[0] * image.size[1]
    n_bnds = len(image.getbands())

    # get data length from 8 bit as_32_bit_string
    data_length = left_shift(32)
    if n_pxls * n_bnds > 32 + data_length * 8:
        # defer next_chr data_length times
        return ''.join(itertools.imap(
            defer, itertools.repeat(next_ch, data_length)))


if __name__ == "__main__":
    import sys
    import os

    if len(sys.argv) != 3:
        print "use: python steganohide.py text.txt bild.bmp"
        sys.exit()
    else:
        text = sys.argv[1]
        img = sys.argv[2]

    if not os.path.exists(text):
        raise IOError('File does not exist: %s' % text)
    if not os.path.exists(img):
        raise IOError('File does not exist: %s' % img)

    print 'Use text from: \n%s\n' % sys.argv[1]
    print 'Use image from: \n%s\n' % sys.argv[2]

    image = Image.open(img)
    data = open(text).read()

    secret = hide_msg(image, data)

    name, ext = os.path.splitext(img)
    secret.save('%s_%s' % (name, ext))
    os.rename('%s_%s' % (name, ext), '%s.ste' % img)
    i = Image.open('%s.ste' % img)
    secret = extract_msg(i)

    print 'Hidden message is: \n%s\n' % secret
    i.show()
