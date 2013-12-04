if __name__ == "__main__":
    import sys, os
    import hmac
    import hashlib
    import base64

    if len(sys.argv)!=3:
        print "use: python steganohide.py text.txt bild.bmp"
        sys.exit()
    else:
        text = sys.argv[1]
        img = sys.argv[2]
        
    if not os.path.exists(text): raise IOError('File does not exist: %s' % text)
    if not os.path.exists(img): raise IOError('File does not exist: %s' % img)
    
    print 'text: %s' % sys.argv[1]
    print 'image: %s' % sys.argv[2]
    
    image = Image.open(img)
    data = open(text).read()
    hmac_pass = 'secret'

    h_mac = hmac.new(hmac_pass, bytes(data), digestmod=hashlib.sha256).digest()
    h_mac+='--:--'+data
    secret = hide_msg(image, h_mac)
    
    name, ext = os.path.splitext(img)
    secret.save('%s_%s' % (name, ext))
    os.rename('%s_%s' % (name, ext), '%s.ste' % img)
    i = Image.open('%s.ste' % img)
    secret = extract_msg(i)
    mac = secret.split('--:--')[0]
    print 'hmac: ' + mac
    data = secret.split('--:--')[1]
    print 'secret: '+ data

    h_mac = hmac.new(hmac_pass, bytes(data), digestmod=hashlib.sha256).digest()
    print 'check hmac: ' + str(h_mac==mac)
    i.show()