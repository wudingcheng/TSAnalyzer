import subprocess
import os

images = os.listdir('../TSResource/images')
# qss = os.listdir('./qss')
f = open('images.qrc', 'w+')
f.write(u'<!DOCTYPE RCC>\n<RCC version="1.0">\n<qresource>\n')

for item in images:
    f.write(u'<file alias="../TSResource/images/' + item + '">../TSResource/images/' + item + '</file>\n')

# for item in qss:
#     f.write(u'<file alias="qss/' + item + '">qss/' + item + '</file>\n')

f.write(u'</qresource>\n</RCC>')
f.close()

# pipe = subprocess.Popen(r'pyrcc4 -o images.py images.qrc', stdout=subprocess.PIPE,
#                         stdin=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08)
