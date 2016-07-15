# Матрёшка

<img src="/resources/matroschka_.png" alt="Matroschka" width="250px">

# About
**Матрёшка** [mɐˈtrʲɵʂkə] is a command-line steganography tool written in pure Python. You can use it to hide and encrypt images or text in the least significant bits of pixels in an image. 
The encryption uses **HMAC-SHA256** to authenticate the hidden data. Therefore the supplied **MAC** password is hashed with **SHA-256** digest to generate the **HMAC-SHA256** key. 
The **MAC** and the message data is furhter encrypted using the **XTEA** algorithm in **CFB** mode (64 bit block cipher) before beeing embedded in the image data. The **SHA-256** hash is created using the 128 high-order bits.

# Note
> This is a fun project. Do not use this for serious encryption purposes!

# Usage


