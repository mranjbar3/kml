import argparse, ctypes, io, time, sys
from PIL import Image
import urllib.request as urllib

parser = argparse.ArgumentParser()
parser.add_argument('--zoom', type=int, default=8, choices=[6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
parser.add_argument('--type', default='708', choices=['708', 'pahneh', 'mahdodeh', 'mozayede', 'tarh', 'marz'])
parser.add_argument('--time_out', type=int, default=1)
args = parser.parse_args()
zoom = args.zoom
key = args.type
if key == 'pahneh':
    key = 'Pahneh'  # پهنه ها
elif key == 'mahdodeh':
    key = 'M10'  # محدوده ها
elif key == 'mozayede':
    key = 'MozayedeInProg'  # مزایده های در حال انجام
elif key == 'tarh':
    key = '12121'  # طرح ها
elif key == 'marz':
    key = '2'  # مرزبندی استانها

if zoom == 6:
    horizontal_min = 39
    horizontal_max = 44
    vertical_min = 24
    vertical_max = 28
elif zoom == 7:
    horizontal_min = 79
    horizontal_max = 87
    vertical_min = 48
    vertical_max = 55
elif zoom == 8:
    horizontal_min = 159
    horizontal_max = 173
    vertical_min = 97
    vertical_max = 110
elif zoom == 9:
    horizontal_min = 318
    horizontal_max = 347
    vertical_min = 194
    vertical_max = 220
elif zoom == 10:
    horizontal_min = 637
    horizontal_max = 692
    vertical_min = 388
    vertical_max = 437
elif zoom == 11:
    horizontal_min = 1274
    horizontal_max = 1380
    vertical_min = 776
    vertical_max = 877
elif zoom == 12:
    horizontal_min = 2548
    horizontal_max = 2769
    vertical_min = 1553
    vertical_max = 1754
elif zoom == 13:
    horizontal_min = 5098
    horizontal_max = 5538
    vertical_min = 3107
    vertical_max = 3509
elif zoom == 14:
    horizontal_min = 10194
    horizontal_max = 11075
    vertical_min = 6213
    vertical_max = 7014
elif zoom == 15:
    horizontal_min = 20391
    horizontal_max = 22149
    vertical_min = 12429
    vertical_max = 14028
elif zoom == 16:
    horizontal_min = 40781
    horizontal_max = 44298
    vertical_min = 24860
    vertical_max = 28055

north = 41.2
south = 24.69
west = 42.15
east = 64.7
hor_n = (east - west) / (horizontal_max - horizontal_min)
ver_n = (north - south) / (vertical_max - vertical_min)

hex_chr = "0123456789abcdef"


def rhex(n):
    str = ""
    for j in range(4):
        str += hex_chr[n >> j * 8 + 4 & 15] + hex_chr[n >> j * 8 & 15]
    return str


def add(n, t):
    i = (n & 65535) + (t & 65535)
    r = ctypes.c_int(n >> 16 ^ 0).value + ctypes.c_int(t >> 16 ^ 0).value + ctypes.c_int(i >> 16 ^ 0).value
    return ctypes.c_int(r << 16 ^ 0).value | i & 65535


def rshift(val, n):
    return (val % 0x100000000) >> n


def rol(n, t):
    return ctypes.c_int(n << t ^ 0).value | rshift(n, 32 - t)


def cmn(n, t, i, r, u, f):
    return add(rol(add(add(t, n), add(r, f)), u), i)


def ff(n, t, i, r, u, f, e):
    return cmn(t & i | ~t & r, n, t, u, f, e)


def gg(n, t, i, r, u, f, e):
    return cmn(t & r | i & ~r, n, t, u, f, e)


def hh(n, t, i, r, u, f, e):
    return cmn(t ^ i ^ r, n, t, u, f, e)


def ii(n, t, i, r, u, f, e):
    return cmn(i ^ (t | ~r), n, t, u, f, e)


def kk(n, t, i):
    return n + t + i


def str2blks(n):
    n = str(n) + hex_chr
    nblk = (len(n) + 8 >> 6) + 1
    blks = []
    for i in range(nblk * 16):
        blks.append(0)
    for i in range(len(n)):
        blks[i >> 2] |= ord(n[i]) << i % 4 * 8
    i += 1
    blks[i >> 2] |= (128 << i % 4 * 8)
    blks[nblk * 16 - 2] = len(n) * 8
    return blks


def calcTile(n):
    x = str2blks(n)
    a = 1732584193
    b = -271733879
    c = -1732584194
    d = 271733878
    for i in range(0, 16, len(x)):
        olda = a
        oldb = b
        oldc = c
        oldd = d
        a = ff(a, b, c, d, x[i + 0], 7, -680876936)
        d = ff(d, a, b, c, x[i + 1], 12, -389564586)
        c = ff(c, d, a, b, x[i + 2], 17, 606105819)
        b = ff(b, c, d, a, x[i + 3], 22, -1044525330)
        a = ff(a, b, c, d, x[i + 4], 7, -176418897)
        d = ff(d, a, b, c, x[i + 5], 12, 1200080426)
        c = ff(c, d, a, b, x[i + 6], 17, -1473231341)
        b = ff(b, c, d, a, x[i + 7], 22, -45705983)
        a = ff(a, b, c, d, x[i + 8], 7, 1770035416)
        d = ff(d, a, b, c, x[i + 9], 12, -1958414417)
        c = ff(c, d, a, b, x[i + 10], 17, -42063)
        b = ff(b, c, d, a, x[i + 11], 22, -1990404162)
        a = ff(a, b, c, d, x[i + 12], 7, 1804603682)
        d = ff(d, a, b, c, x[i + 13], 12, -40341101)
        c = ff(c, d, a, b, x[i + 14], 17, -1502002290)
        b = ff(b, c, d, a, x[i + 15], 22, 1236535329)
        a = gg(a, b, c, d, x[i + 1], 5, -165796510)
        d = gg(d, a, b, c, x[i + 6], 9, -1069501632)
        c = gg(c, d, a, b, x[i + 11], 14, 643717713)
        b = gg(b, c, d, a, x[i + 0], 20, -373897302)
        a = gg(a, b, c, d, x[i + 5], 5, -701558691)
        d = gg(d, a, b, c, x[i + 10], 9, 38016083)
        c = gg(c, d, a, b, x[i + 15], 14, -660478335)
        b = gg(b, c, d, a, x[i + 4], 20, -405537848)
        a = gg(a, b, c, d, x[i + 9], 5, 568446438)
        d = gg(d, a, b, c, x[i + 14], 9, -1019803690)
        c = gg(c, d, a, b, x[i + 3], 14, -187363961)
        b = gg(b, c, d, a, x[i + 8], 20, 1163531501)
        a = gg(a, b, c, d, x[i + 13], 5, -1444681467)
        d = gg(d, a, b, c, x[i + 2], 9, -51403784)
        c = gg(c, d, a, b, x[i + 7], 14, 1735328473)
        b = gg(b, c, d, a, x[i + 12], 20, -1926607734)
        a = hh(a, b, c, d, x[i + 5], 4, -378558)
        d = hh(d, a, b, c, x[i + 8], 11, -2022574463)
        c = hh(c, d, a, b, x[i + 11], 16, 1839030562)
        b = hh(b, c, d, a, x[i + 14], 23, -35309556)
        a = hh(a, b, c, d, x[i + 1], 4, -1530992060)
        d = hh(d, a, b, c, x[i + 4], 11, 1272893353)
        c = hh(c, d, a, b, x[i + 7], 16, -155497632)
        b = hh(b, c, d, a, x[i + 10], 23, -1094730640)
        a = hh(a, b, c, d, x[i + 13], 4, 681279174)
        d = hh(d, a, b, c, x[i + 0], 11, -358537222)
        c = hh(c, d, a, b, x[i + 3], 16, -722521979)
        b = hh(b, c, d, a, x[i + 6], 23, 76029189)
        a = hh(a, b, c, d, x[i + 9], 4, -640364487)
        d = hh(d, a, b, c, x[i + 12], 11, -421815835)
        c = hh(c, d, a, b, x[i + 15], 16, 530742520)
        b = hh(b, c, d, a, x[i + 2], 23, -995338651)
        a = ii(a, b, c, d, x[i + 0], 6, -198630844)
        d = ii(d, a, b, c, x[i + 7], 10, 1126891415)
        c = ii(c, d, a, b, x[i + 14], 15, -1416354905)
        b = ii(b, c, d, a, x[i + 5], 21, -57434055)
        a = ii(a, b, c, d, x[i + 12], 6, 1700485571)
        d = ii(d, a, b, c, x[i + 3], 10, -1894986606)
        c = ii(c, d, a, b, x[i + 10], 15, -1051523)
        b = ii(b, c, d, a, x[i + 1], 21, -2054922799)
        a = ii(a, b, c, d, x[i + 8], 6, 1873313359)
        d = ii(d, a, b, c, x[i + 15], 10, -30611744)
        c = ii(c, d, a, b, x[i + 6], 15, -1560198380)
        b = ii(b, c, d, a, x[i + 13], 21, 1309151649)
        a = ii(a, b, c, d, x[i + 4], 6, -145523070)
        d = ii(d, a, b, c, x[i + 11], 10, -1120210379)
        c = ii(c, d, a, b, x[i + 2], 15, 718787259)
        b = ii(b, c, d, a, x[i + 9], 21, -343485551)
        a = add(a, olda)
        b = add(b, oldb)
        c = add(c, oldc)
        d = add(d, oldd)
    return rhex(a) + rhex(b) + rhex(c) + rhex(d)


'''f = open("cadaster_pahneh.kml", "w")
f.write("<?xml version='1.0' encoding='ASCII'?>\n" +
        "<kml xmlns:atom='http://www.w3.org/2005/Atom' xmlns:gx='http://www.google.com/kml/ext/2.2' xmlns='http://www.opengis.net/kml/2.2'>\n" +
        "  <Document>\n    <name>Google Road root</name>\n    <name>DOC_2_0_0</name>")'''
full_image = Image.new('RGB', (0, 0))
full_cnt = (horizontal_max - horizontal_min) * (vertical_max - vertical_min)

for i in range(horizontal_min, horizontal_max):
    img_x = full_image.size[0]
    img_y = 0
    for j in range(vertical_min, vertical_max):
        '''stri = "    <GroundOverlay>\n" + \
               "      <name>pahneh_La_" + str(i) + "_" + str(j) + "</name>\n" + \
               "      <drawOrder>2</drawOrder>\n" + \
               "      <Icon>\n" + \
               "        <href>"'''
        url_img = "https://map.mimt.gov.ir/"
        if key == '708':
            url_img += 'SafaTGBaseMap'
        else:
            url_img += "SafaTGLive"
        url_img += "/maptile.ashx?x=" + str(i) + "&amp;y=" + str(j) + "&amp;z=" + str(zoom) + "&amp;Key=" + key + \
                   "&amp;r=" + calcTile(kk(zoom, i, j))
        '''stri += url_img + "</href>\n" + \
                "      </Icon>\n" + \
                "      <LatLonBox>\n" + \
                "        <north>" + str(north - ver_n * (j - vertical_min)) + "</north>\n" + \
                "        <south>" + str(north - ver_n * (j + 1 - vertical_min)) + "</south>\n" + \
                "        <east>" + str(west + hor_n * (i + 1 - horizontal_min)) + "</east>\n" + \
                "        <west>" + str(west + hor_n * (i - horizontal_min)) + "</west>\n" + \
                "      </LatLonBox>\n" + \
                "    </GroundOverlay>\n"
        f.write(stri)'''
        url_img = url_img.replace('amp;', '')
        try:
            fd = urllib.urlopen(url_img, timeout=args.time_out)
            image_file = io.BytesIO(fd.read())
            im = Image.open(image_file)
        except:
            im = Image.new('RGB', (256, 256))
        tmp = full_image.copy()
        full_image = Image.new('RGB', (img_x + im.size[0], max(tmp.size[1], img_y + im.size[1])))
        full_image.paste(tmp, (0, 0))
        full_image.paste(im, (img_x, img_y))
        img_y += im.size[1]
        download_pic = (i - horizontal_min) * (vertical_max - vertical_min) + (j - vertical_min + 1)
        b = 'download ' + str(download_pic) + ' from ' + str(full_cnt) + ' this equal ' + \
            str(int(download_pic / full_cnt * 100)) + '%'
        sys.stdout.write('\r' + b)
    full_image.save('cadaster_' + args.type + '.png')
'''f.write("  </Document>\n</kml>")
f.close()'''
full_image.save('cadaster_' + args.type + '.png')
print('\r\nDownload Completed.\r\nImages save in cadaster_' + args.type + '.png file')
