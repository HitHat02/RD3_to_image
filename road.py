import bitstring
from PIL import Image
import numpy as np
import os


class roadDrawing():

    def __init__(self, DIRNAME, BASENAME):
        self.hResolution = 2 ** 4
        self.wResolution = 1
        self.encodedBit = 3
        self.byteLen = 1
        self.DIRNAME = DIRNAME
        self.BASENAME = BASENAME

    def makeImg(self, file_langth):

        path = os.path.join(self.DIRNAME, self.BASENAME[:-4]+'.rst')
        with open(path, 'rb') as f:
            data = f.read()

        dataSize = len(data)

        print("mkeImage", dataSize/3/file_langth)

        if dataSize/3/file_langth > 1270 and dataSize/3/file_langth < 1285:
            Hsize = 1280

        elif dataSize/3/file_langth > 930 and dataSize/3/file_langth < 933:
            Hsize = 1280

        else:
            Hsize = 2048

        heigthSize = int(Hsize / self.hResolution)

        realHeigthSize = Hsize * self.encodedBit

        realWeithSize = int(dataSize / realHeigthSize)

        weithSize = int(realWeithSize / self.wResolution)

        imageSize = int(weithSize * heigthSize)

        print('realHeigthSize',realHeigthSize ,'\n','realWeithSize',realWeithSize)

        t = ['uint:24']
        ii = np.zeros(imageSize)

        indexList = [(w * realHeigthSize) + h + self.hResolution for w in range(0, realWeithSize, self.wResolution) for h in
                     range(0, realHeigthSize,
                           self.byteLen * self.hResolution)]  #:(w*realHeigthSize)+h+(byteLen*encodedBit)+hResolution

        aa = bitstring.Bits(bytes=[data[i] for i in indexList],
                            length=8 * self.encodedBit * self.byteLen * imageSize)

        ii = aa.unpack(','.join(t * self.byteLen * imageSize))

        b = np.reshape(ii[(len(ii) % int(heigthSize)):], (-1, int(heigthSize)))
        print(b.shape)

        c = b / b.max() * 255
        print(c.shape)

        img = Image.fromarray(c[::-1])
        if img.mode != 'RGB':
            img = img.convert('RGB')

        deg_image = img.transpose(Image.ROTATE_270)
        print(deg_image.size[0])

        return deg_image