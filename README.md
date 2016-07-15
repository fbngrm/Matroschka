# Матрёшка

<img src="/resources/matroschka.png" alt="Matroschka" width="250px">

# About
**Матрёшка** [mɐˈtrʲɵʂkə] is a command-line steganography tool written in pure Python. You can use it to hide and encrypt images or text in the least significant bits of pixels in an image. 

#Encryption
The encryption uses **HMAC-SHA256** to authenticate the hidden data. Therefore the supplied **MAC** password is hashed with **SHA-256** digest to generate the **HMAC-SHA256** key. 
The **MAC** and the message data is further encrypted using the **XTEA** algorithm in **CFB** mode running **32 iterations**, before beeing embedded in the image data. The **SHA-256** hash for the **XTEA** key is created using the **128 high-order bits** of the supplied password. A **random 8 byte seed** is used in the **CFB 64 bit block cipher**.

#Decryption
The random seed is appended to the hidden secret and is used with the user supplied password to decrypt the hidden message using **XTEA block cipher** according to the encryption process. Further the decrypted secret is authenticated by comparing the embeded hmac hash with the **HMAC-SHA256** of the extracted hidden message and the user supplied mac password.

# Note
> This is a fun project. Do not use this for serious encryption purposes!

# Usage
Only losless image formats are supported. Therefore It is recommended to use PNG or BMP images to hide your secret. The secret can be either an text file with the `.txt` extension or an image with the `.png` extension and format. 

> Note: If your image contains transparent pixels, most likely artifacts will be visible after embedding data. This is caused by the manipulation of the least-significant bit in every pixels color channels.

**Hide Secret**

```bash 
python matroschka.py -hide -m <mac-password> -k <password> <secret> <image>
```

**Reveal Secret**

```bash 
python matroschka.py -open -m <mac-password> -k <password> <image>
```

**Example**

*matroschka_medium.png* gets hidden and encrypted in *matroschka_big.png*

```bash 
python matroschka.py -hide -m foo -k bar resources/matroschka_medium.png resources/matroschka_big.png
```

Decrypting the image will save the extracted image in resources/secret-image.png

```bash 
python matroschka.py -open -m foo -k bar resources/matroschka_big.png
```

#License
GNU General Public License 3.0
