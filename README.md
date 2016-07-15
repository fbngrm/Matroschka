# Матрёшка

<img src="/resources/matroschka.png" alt="Matroschka" width="250px">

# About
**Матрёшка** [mɐˈtrʲɵʂkə] is a command-line steganography tool written in pure Python. You can use it to hide and encrypt images or text in the least significant bits of pixels in an image. 
The encryption uses **HMAC-SHA256** to authenticate the hidden data. Therefore the supplied **MAC** password is hashed with **SHA-256** digest to generate the **HMAC-SHA256** key. 
The **MAC** and the message data is furhter encrypted using the **XTEA** algorithm in **CFB** mode before beeing embedded in the image data. The **SHA-256** hash for the **XTEA** key is created using the 128 high-order bits. A random 8 byte sed is used in the CFB 64 bit block cipher.

# Note
> This is a fun project. Do not use this for serious encryption purposes!

# Usage


