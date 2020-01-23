import requests,re,time,os,threading,multiprocessing,sys,tkinter
from bs4 import BeautifulSoup
header={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36 Edg/79.0.309.63'}
class bnComic:
	def __init__(self):
		self.comicDict={}
		self.url='https://m.bnmanhua.com'
		self.kw=input('请输入要下载的漫画:')
		os.mkdir(self.kw)
		self.comicUrl=self.searchComic(self.kw)
		self.pageList=self.returnPage(self.comicUrl)
	def searchComic(self,kw):
		r=requests.post(self.url+'/index.php?m=vod-search',{'wd':self.kw})
		comic=re.search('<a class=\"vbox_t\" href=\"(.*)\" title=\"(.*)\">',r.text)
		r.close()
		if not comic:
			print('没有漫画,请检查漫画名称')
			return
		return self.url+comic.group(1)
	def returnPage(self,u):
		r=requests.get(u)
		soup=BeautifulSoup(r.text,'html.parser')
		r.close()
		if soup.body.font:
			print('此漫画受版权限制,禁止下载')
			return
		return [self.url+x.attrs['href'] for x in soup.ul.find_all('a')]
	def picDict(self,u):
		r=requests.get(u,headers=header)
		soup=BeautifulSoup(r.text,'html.parser')
		b=re.findall(r'\[(.*)\]',soup.body.script.string.split(';')[1])
		if 'https:' in re.sub('\"','',eval(re.sub(r'\\','',repr(b[0])))).split(','):
			self.comicDict[soup.title.text.split('-')[1]]=re.sub('\"','',eval(re.sub(r'\\','',repr(b[0])))).split(',')
		else:
			self.comicDict[soup.title.text.split('-')[1]]=['https://img.yaoyaoliao.com/'+x for x in re.sub('\"','',eval(re.sub(r'\\','',repr(b[0])))).split(',')]
		r.close()
	def saveComic(self,part):
		c=0
		os.mkdir('.\\'+self.kw+'\\'+part[0])
		for pic in part[1]:
			c+=1
			r=requests.get(pic)
			if pic[-1]=='0':
				f=open('.\\'+self.kw+'\\'+part[0]+'\\'+str(c)+'.png','wb')
				f.write(r.content)
				r.close()
				f.close()
			f=open('.\\'+self.kw+'\\'+part[0]+'\\'+str(c)+'.jpg','wb')
			f.write(r.content)
			r.close()
			f.close()
		return
	def run(self):
		for page in self.pageList:
			t=threading.Thread(target=self.picDict,args=(page,))
			t.daemon=1
			t.start()
		time.sleep(10)
		print('正在下载')
		for part in self.comicDict.items():
			t=threading.Thread(target=self.saveComic,args=(part,))
			t.daemon=1
			t.start()
		print('下载完成')
manhua=bnComic()
manhua.run()