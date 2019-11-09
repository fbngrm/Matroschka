try:
    import Image
except:
    from PIL import Image

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


def check_hmac(mac, data):
    """
    Check if the given hmac ist valid by creating
    a new hmac with the supplied password and the data.
    """
    h_mac = hmac.new(args['m'], bytes(data), digestmod=hashlib.sha256).digest()
    print 'HMAC validation: \n%s\n' % str(h_mac == mac)


def hash_128_bit_pass(passwd):
    """
    Create a hash of the given password using the
    SHA-256 digest algorithm.
    """
    h = hashlib.sha256()
    h.update(passwd)
    return h.hexdigest()[:16]


def crypt(key, data, iv):
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


def encrypt(data_type):
    # create hmac from the supplied mac password hashed with SHA-256
    # digest algorithm and the supllied image or text data
    h_mac = create_hmac(args['m'], bytes(data))

    # join hmac and message data
    secret = '%s--:--%s' % (h_mac, data)

    # create a SHA-256 hash of the high-order 128 bit of the given password
    key = hash_128_bit_pass(args['k'])

    # encrypt the data using XTEA algorithm in CFB mode with the 128 bit
    # SHA-256 hash of the password as key and a random seed of 8 bytes
    iv = os.urandom(8)
    encrypted_secret = crypt(key, secret, iv)

    # prepend the iv to the encrypted data because it is required for
    # the decryption and hide the data in the image
    matroschka = stg.hide_msg(image, '%s--:--%s--:--%s' % (
        data_type, iv, encrypted_secret))

    # save the image containing the embeded and encrypted
    # data to disk with the extension .ste
    matroschka.save(args['image'])

    print "successfully encrypted your secret message"
    matroschka.show()


def decrypt():
    # extract and authenticate the hidden message in the image data
    image = Image.open(args['image'])
    matroschka = stg.extract_msg(image)

    if matroschka is None:
        print "No message was extracted"
        return 1

    # get the 8 byte iv and the encrypted secret from the image data
    data_type, iv, encrypted_secret = matroschka.split('--:--')

    # create a SHA-256 hash of the high-order 128 bit of the given password
    key = hash_128_bit_pass(args['k'])

    # decrypt the secret with the iv and the supplied password
    decrypted_secret = crypt(key, encrypted_secret, iv)

    # split hmac and message data
    mac, data = decrypted_secret.split('--:--')

    if data_type == 'image':
        ipath = "resources/secret-image.png"
        print "the secret image is stored under: " + ipath
        fh = open(ipath, "wb")
        fh.write(data.decode('base64'))
        fh.close()
        Image.open(ipath).show()
    else:
        print 'The hidden message is: \n%s\n' % data

    print 'HMAC hex is: \n%s\n' % mac.encode('hex')
    check_hmac(mac, data)


if __name__ == '__main__':
    # Add the command-line arguments
    parser = argparse.ArgumentParser(description='Description of your program')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-hide', help='encrypt', action='store_true')
    group.add_argument('-open', help='decrypt', action='store_true')
    parser.add_argument(
        '-m', metavar='macpasswd', help='macpassword', required=True)
    parser.add_argument('-k', metavar='passwd', help='password', required=True)
    parser.add_argument('data', nargs='?')
    parser.add_argument('image')

    args = vars(parser.parse_args())

    # Check if the required args are supplied
    # If not print user feedback and exit
    if args['data']:
        if args['data'].endswith('png') or args['data'].endswith('jpg'):
            import base64
            data_type = 'image'
            with open(args['data'], "rb") as imageFile:
                data = base64.b64encode(imageFile.read())
        elif args['data'].endswith('txt'):
            data_type = 'text'
            data = read_text(args['data'])
        else:
            print "need secret message either as .txt or .png file"
            sys.exit(0)

    if args['image']:
        image = read_image(args['image'])
    else:
        print "need image to embed data"
        sys.exit(0)

    # encrypt the secret message
    if args['hide']:
        encrypt(data_type)

    # decrypt the secret message
    if args['open']:
        decrypt()
