import Image
import argparse
import hashlib
import hmac
import os
import steganohide as stg
import xtea
import sys


def create_hmac(mac_pass, msg_bytes):
    """
    Create an hmac keyed hash for the given message
    using the SHA-256 digest algorithm.
    """
    return hmac.new(
        mac_pass, msg_bytes, digestmod=hashlib.sha256).digest()


def save_img(img):
    name, ext = os.path.splitext(img)
    secret.save('%s_%s' % (name, ext))
    os.rename('%s_%s' % (name, ext), '%s.ste' % img)


def get_msg(img):
    """
    Extract the hidden message fro the given image.
    Authenticate the hidden message by validating the
    hmac hash sliced from the hidden message.
    """
    i = Image.open('%s.ste' % img)
    secret = stg.extract_msg(i)
    mac = secret.split('--:--')[0]
    print 'HMAC hex is: \n%s\n' % mac.encode('hex')
    data = secret.split('--:--')[1]
    print 'The hidden message is: \n%s\n' % data
    check_hmac(mac)
    i.show()


def check_hmac(hmac):
    """
    Check if the given hmac ist valid by creating
    a new hmac with the supplied password and the data.
    """
    h_mac = hmac.new(args['m'], bytes(data), digestmod=hashlib.sha256).digest()
    print 'HMAC validation: %s\n' % str(h_mac == hmac)


def hash_128_bit_pass(passwd):
    """
    Create a hash of the given password using the
    SHA-256 digest algorithm.
    """
    h = hashlib.sha256()
    h.update(passwd)
    return h.hexdigest()[:16]


def crypt(data, key, iv):
    """
    Encrypt or decrypt the given data with the given
    key using the XTEA algorithm in CFB mode.
    """
    return xtea.crypt(key, data, iv)


def read_image(image_path):
    """
    Read the image data of the given path
    and return an Image object
    """
    if not os.path.exists(image_path):
        raise IOError('File does not exist: %s' % image_path)
    else:
        return Image.open(image_path)


def read_text(text_path):
    """
    Read the content of the given text file and
    return the content as a string
    """
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

    # create hmac from the supplied mac password hashed with SHA-256 
    # digest algorithm and the supllied image or text data 
    h_mac = create_hmac(args['m'], bytes(data))

    #  
    secret = stg.hide_msg(image, '%s--:--%s' % (h_mac, data))

    # save the image containing the embeded and encrypted 
    # data to disk with the extension .ste
    save_img(args['image'])

    # extract and authenticate the hidden message in the image data
    get_msg(args['image'])

    # create a SHA-256 hash of the high-order 128 bit of the given password
    key = hash_128_bit_pass(args['k'])

    # encrupy the data using the XTEA algorithm in CFB mode with the 128 bit
    # SHA-256 hash of the password as key
    encrypted_data = crypt(data, key)
    iv = os.urandom(8)
    print xtea.crypt(key, encrypted_data, iv)
    print xtea.crypt(key, encrypted_data, iv) == data

