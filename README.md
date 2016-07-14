# Матрёшка

<img src="/resources/matroschka.png" alt="Matroschka" width="250px">

# About
**Матрёшка** is a command-line steganography tool written in pure Python. You can use it to hide and encrypt images or text in the least significant bits of pixels in an image. 
The encryption uses **HMAC-SHA256**. Therefore the supplied **MAC** password is hashed with **SHA-256** to generate the **HMAC-SHA256** key. The **MAC** and the message data is encrypted using the **XTEA** algorithm in **CFB** mode before beeing embedded in the image data. The **SHA-256** hash is created using the 128 high-order bits.

# Note
> This is a fun project. Do not use this for serious encryption purposes!

# Usage


