import requests
from bs4 import BeautifulSoup

data1=[]
row = []

# for sigungu, dong, bun, ji in zip(sigungu, dong,bun, ji):

#   url="http://apis.data.go.kr/1613000/BldRgstService_v2/getBrRecapTitleInfo?sigunguCd=" + str(sigungu) + "&bjdongCd=" + str(dong) + "&platGbCd=&bun=" + str(bun) + "&ji=" + str(ji) + "&ServiceKey=본인의 인증키"
  #print(url)

url="http://apis.data.go.kr/1613000/BldRgstService_v2/getBrRecapTitleInfo?sigunguCd=11680&bjdongCd=10300&bun=0012&ji=0000&ServiceKey=0SOpqNrCf4jV3RuThV6qvS0N%2FgFlHU5EbIpwYUajVZ512g%2BKfG3w%2FJ5h%2Be4xtJcUuZwiKIsAhXgYLqHz3FLe5Q%3D%3D"
result=requests.get(url)

soup=BeautifulSoup(result.text, 'lxml-xml')
items=soup.find_all('item')

print(items)