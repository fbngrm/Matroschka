""" 
XTEA Block Encryption Algorithm

Original Code: http://code.activestate.com/recipes/496737/
Algorithm:     http://www.cix.co.uk/~klockstone/xtea.pdf 

    >>> import os
    >>> x = xtea.xtea()
    >>> iv = 'ABCDEFGH'
    >>> z = x.crypt('0123456789012345','Hello There',iv)
    >>> z.encode('hex')
    'fe196d0a40d6c222b9eff3'
    >>> x.crypt('0123456789012345',z,iv)
    'Hello There'

Modified to use CBC - Steve K:
    >>> import xtea
    >>> x = xtea.xtea()
    >>> #set up your key and IV then...
    >>> x.xtea_cbc_decrypt(key, iv, data, n=32, endian="!")

""" 
import struct

TEA_BLOCK_SIZE = 8
TEA_KEY_SIZE   = 16


def xtea_encrypt(key,block,n=32,endian="!"):
    """
        Encrypt 64 bit data block using XTEA block cypher
        * key = 128 bit (16 char) 
        * block = 64 bit (8 char)
        * n = rounds (default 32)
        * endian = byte order (see 'struct' doc - default big/network) 

        >>> z = xtea_encrypt('0123456789012345','ABCDEFGH')
        >>> z.encode('hex')
        'b67c01662ff6964a'

        Only need to change byte order if sending/receiving from 
        alternative endian implementation 

        >>> z = xtea_encrypt('0123456789012345','ABCDEFGH',endian="<")
        >>> z.encode('hex')
        'ea0c3d7c1c22557f'

    """
    v0, v1 = struct.unpack(endian + "2L", block)
    k = struct.unpack(endian + "4L", key)
    sum, delta, mask = 0L, 0x9e3779b9L, 0xffffffffL
    for round in range(n):
        v0 = (v0 + (((v1<<4 ^ v1>>5) + v1) ^ (sum + k[sum & 3]))) & mask
        sum = (sum + delta) & mask
        v1 = (v1 + (((v0<<4 ^ v0>>5) + v0) ^ (sum + k[sum>>11 & 3]))) & mask
    return struct.pack(endian + "2L", v0, v1)

def crypt(key,data,iv='\00\00\00\00\00\00\00\00',n=32):
    """
        Encrypt/decrypt variable length string using XTEA cypher as
        key generator (OFB mode)
        * key = 128 bit (16 char) 
        * iv = 64 bit (8 char)
        * data = string (any length)

        >>> import os
        >>> key = os.urandom(16)
        >>> iv = os.urandom(8)
        >>> data = os.urandom(10000)
        >>> z = crypt(key,data,iv)
        >>> crypt(key,z,iv) == data
        True

    """
    
    def keygen(key,iv,n):
        """
        encrypt the key and create a generator for all 8 bit blocks 
        in the 64 bit block of the encrypted key
        """
        while True:
            # encrypt 64 bit block
            # encrypt the key with initialization vector
            # use the partially(64bit) encrypted key as initialization vector 
            # for the next block after the first iteration of the while loop
            iv = xtea_encrypt(key,iv,n)
            # for 8 bit in 64 bit
            for k in iv:
                yield ord(k)
                
    # map - get list of ordinals for all chars in data
    # keygen - create a generator(8 bit steps) of the encrypted key
    # zip - crate tuples for a char(8bit) and 8bit of the key
    # x^y xor the created tuples and cast them to 8 bit
    xor = [ chr(x^y) for (x, y) in zip(map(ord, data), keygen(key, iv, n)) ]
    return "".join(xor)

def xtea_decrypt(key,block,n=32,endian="!"):
    """
        Decrypt 64 bit data block using XTEA block cypher
        * key = 128 bit (16 char) 
        * block = 64 bit (8 char)
        * n = rounds (default 32)
        * endian = byte order (see 'struct' doc - default big/network) 

        >>> z = 'b67c01662ff6964a'.decode('hex')
        >>> xtea_decrypt('0123456789012345',z)
        'ABCDEFGH'

        Only need to change byte order if sending/receiving from 
        alternative endian implementation 

        >>> z = 'ea0c3d7c1c22557f'.decode('hex')
        >>> xtea_decrypt('0123456789012345',z,endian="<")
        'ABCDEFGH'
    """
    v0,v1 = struct.unpack(endian+"2L",block)
    k = struct.unpack(endian+"4L",key)
    delta,mask = 0x9e3779b9L,0xffffffffL
    sum = (delta * n) & mask
    for round in range(n):
        v1 = (v1 - (((v0<<4 ^ v0>>5) + v0) ^ (sum + k[sum>>11 & 3]))) & mask
        sum = (sum - delta) & mask
        v0 = (v0 - (((v1<<4 ^ v1>>5) + v1) ^ (sum + k[sum & 3]))) & mask
    return struct.pack(endian+"2L",v0,v1)

def xtea_cbc_decrypt(key, iv, data, n=32, endian="!"):
    """
        Decrypt a data buffer using cipher block chaining mode
        Written by Steve K
    """
    global TEA_BLOCK_SIZE
    size = len(data)
    if (size % TEA_BLOCK_SIZE != 0):
        raise Exception("Size of data is not a multiple of TEA \
                        block size (%d)" % (TEA_BLOCK_SIZE))
    decrypted = ""
    i = 0
    while (i < size):
        result = xtea_decrypt(key,
                              data[i:i + TEA_BLOCK_SIZE],
                              n, endian)

        j = 0
        while (j < TEA_BLOCK_SIZE):
            decrypted += chr(ord(result[j]) ^ ord(iv[j]))
            j += 1

        iv = data[i:i + TEA_BLOCK_SIZE]
        i += TEA_BLOCK_SIZE
    return decrypted.strip(chr(0))

def xtea_cbc_encrypt(key, iv, data, n=32, endian="!"):
    """
        Encrypt a data buffer using cipher block chaining mode
        Written by ztwaker
    """
    global TEA_BLOCK_SIZE
    size = len(data)
    #alignment
    if (size % TEA_BLOCK_SIZE != 0):
        data += chr(0) * (TEA_BLOCK_SIZE-(size%TEA_BLOCK_SIZE))
    encrypted = ""
    i = 0
    while (i < size):
        block = ""
        j = 0
        while (j < TEA_BLOCK_SIZE):
            block += chr(ord(data[i+j]) ^ ord(iv[j]))
            j += 1
        
        encrypted += xtea_encrypt(key,
                              block,
                              n, endian)
        
        iv = encrypted[i:i + TEA_BLOCK_SIZE]
        i += TEA_BLOCK_SIZE
    return encrypted


#testing
if __name__ == '__main__':
    import os
    import random
    data = os.urandom(random.randint(0x000000001, 0x00001000))
    key  = os.urandom(TEA_KEY_SIZE)
    iv1  = iv2 = os.urandom(TEA_BLOCK_SIZE)
    print data == xtea_cbc_decrypt(key, iv2, xtea_cbc_encrypt(key, iv1, data))
    
    
