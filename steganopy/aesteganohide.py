import Image
import argparse
import hashlib
import hmac
import os
import steganohide as stg
import xtea
import sys


def create_hmac(mac_pass, msg_bytes):
    return hmac.new(
        mac_pass, msg_bytes, digestmod=hashlib.sha256).digest()


def save_img(img):
    name, ext = os.path.splitext(img)
    secret.save('%s_%s' % (name, ext))
    os.rename('%s_%s' % (name, ext), '%s.ste' % img)


def get_msg(img):
    i = Image.open('%s.ste' % img)
    secret = stg.extract_msg(i)
    mac = secret.split('--:--')[0]
    print 'HMAC hex is: \n%s\n' % mac.encode('hex')
    data = secret.split('--:--')[1]
    print 'The hidden message is: \n%s\n' % data
    check_hmac(mac)
    i.show()


def check_hmac(mac):
    h_mac = hmac.new(args['m'], bytes(data), digestmod=hashlib.sha256).digest()
    print 'HMAC validation: \n%s\n' % str(h_mac == mac)


def hash_128_bit_pass(passwd):
    h = hashlib.sha256()
    h.update(passwd)
    return h.hexdigest()[:16]


def crypt(data, key):
    iv = os.urandom(8)
    z = xtea.crypt(key, data, iv)
    print xtea.crypt(key, z, iv)
    print xtea.crypt(key, z, iv) == data


def read_image(image_path):
    """
    Read the image data of the given path and return an Image object
    """
    if not os.path.exists(image_path):
        raise IOError('File does not exist: %s' % image_path)
    else:
        return Image.open(image_path)


def read_text(text_path):
    """
    Read the content of the given text file and return the content as a string"""
    if not os.path.exists(text_path):
            raise IOError('File does not exist: %s' % text_path)
    return open(text_path).read()


if __name__ == '__main__':
    # Add the command-line arguments
    parser = argparse.ArgumentParser(description='Description of your program')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', help='encrypt', action='store_true')
    group.add_argument('-d', help='decrypt', action='store_true')
    parser.add_argument(
        '-m', metavar='macpasswd', help='macpassword', required=True)
    parser.add_argument('-k', metavar='passwd', help='password', required=True)
    parser.add_argument('data', nargs='?')
    parser.add_argument('image')

    args = vars(parser.parse_args())

    # Check if the required args are supplied
    # If not print user feedback and exit
    if args['data']:
        data = read_text(args['data'])
    else:
        print "need data to embed - either text or image"
        sys.exit(0)

    if args['image']:
        image = read_image(args['image'])
    else:
        print "need image to embed data"
        sys.exit(0)

    h_mac = create_hmac(args['m'], bytes(data))
    secret = stg.hide_msg(image, '%s--:--%s' % (h_mac, data))

    save_img(args['image'])
    get_msg(args['image'])

    key = hash_128_bit_pass(args['k'])
    iv = crypt(data, key)
