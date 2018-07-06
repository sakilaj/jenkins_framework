#!/usr/bin/python
import re
line1 = ['PROJ-WDS_16-011261-R9.0_D3_31']
line2 = ''.join(('"','%s' %line1,'"'))
line3 = re.sub('\'', '', line2)
line4 = re.sub('\[', '', line3)
line5 = re.sub('\]', '', line4)
line6 = re.sub('"', '', line5)
print(line6)
