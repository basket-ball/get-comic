import requests,re,time,os,threading,sys,tkinter
from tkinter import ttk,messagebox,filedialog
from bs4 import BeautifulSoup

url='https://m.bnmanhua.com'
class bnComic(tkinter.Tk):
	def __init__(self):
		super().__init__()
		self.comicDict={}
		self.pageList=[]
		self.urlData={}
		self.title('漫画下载')
		self.geometry('960x525')
		self.createUI()
	def createUI(self):
		self.topFrame=tkinter.Frame(self)
		self.topFrame.pack(fill='x',side='top')
		self.middleFrame=tkinter.Frame(self)
		self.middleFrame.pack(fill='x')
		self.scrollbar=tkinter.Scrollbar(self.middleFrame)
		self.bottomFrame=tkinter.Frame(self)
		self.bottomFrame.pack(fill='x',side='bottom')
		self.pageBox=tkinter.Listbox(self.middleFrame,selectmode=tkinter.EXTENDED,height=26,width=65)
		self.pageBox.pack(side=tkinter.LEFT)
		self.scrollbar.pack(side='left',fill='y')
		self.pageBox['yscrollcommand']=self.scrollbar.set
		self.scrollbar['command']=self.pageBox.yview
		self.kwEntry=tkinter.Entry(self.topFrame)
		self.kwEntry.grid(row=0,column=1)
		self.l1=tkinter.Label(self.topFrame,text='关键字:').grid(row=0,column=0)
		self.l2=tkinter.Label(self.topFrame,text='搜索结果:').grid(row=0,column=3)
		self.searchButton=tkinter.Button(self.topFrame,text='搜索',command=lambda:self.runthread(self.searchComic,self.kwEntry.get())).grid(row=0,column=2)
		self.downButton=tkinter.Button(self.topFrame,text='下载所有',command=lambda:self.runthread(self.saveComic,self.comicDict)).grid(row=0,column=5)
		self.comicList=ttk.Combobox(self.topFrame,height=8,width=40)
		self.comicList.grid(row=0,column=4)
		self.comicList.bind("<<ComboboxSelected>>",lambda x:self.runthread(self.returnPage,self.urlData[self.comicList.get()]))
		self.progress=ttk.Progressbar(self.bottomFrame,length=100,maximum=100.0)
		self.progress.pack(side=tkinter.RIGHT)
		self.l3=tkinter.Label(self.bottomFrame)
		self.l3.pack(side=tkinter.RIGHT)
	def searchComic(self,kw):
		self.l3['text']='正在搜索关键字'
		self.progress['value']=0.0
		self.comicList.set('')
		self.comicList['values']=''
		self.urlData={}
		r=requests.post(url+'/index.php?m=vod-search-pg-1-wd-'+kw+'.html')
		soup=BeautifulSoup(r.text,'html.parser')
		if not soup.find_all(name='li',attrs={'class':'vbox'}):
			self.progress['value']=0.0
			self.l3['text']=''
			raise messagebox.showerror('ERROR','无此漫画,请检查漫画名称')
		v=int(soup.body.find_all(name='em',attrs={'class':'num'})[0].string.split('/')[1])+1
		for p in range(1,v):
			r=requests.post(url+'/index.php?m=vod-search-pg-'+str(p)+'-wd-'+kw+'.html')
			soup=BeautifulSoup(r.text,'html.parser')
			pageNumList=soup.find_all(name='li',attrs={'class':'vbox'})
			for x in pageNumList:
				self.progress['value']+=100/(len(pageNumList)*(v-1))
				self.urlData[x.a['title']]=url+x.a['href']
		self.comicList['values']=[x[0] for x in dict(sorted(self.urlData.items(),key=lambda d:d[1],reverse=True)).items()]
		time.sleep(0.1)
		self.l3['text']=''
		self.progress['value']=0.0
	def returnPage(self,u):
		global ff
		self.progress['value']=0.0
		self.l3['text']='正在返回章节'
		self.pageBox.delete(0,tkinter.END)
		r=requests.get(u)
		soup=BeautifulSoup(r.text,'html.parser')
		r.close()
		if soup.body.font:
			self.progress['value']=0.0
			self.l3['text']=''
			raise messagebox.showerror('ERROR','漫画受版权限制,禁止下载')
		self.pageList=[url+x.attrs['href']+'-'+x.string for x in soup.ul.find_all('a')]
		ff=len(self.pageList)
		for l in self.pageList:
			self.pageBox.insert(tkinter.END,l)
			t=threading.Thread(target=self.picDict,args=(l,))
			self.progress['value']+=100/ff
			t.start()
		self.progress['value']=0.0
		self.l3['text']=''
	def picDict(self,u):
		r=requests.get(u.split('-')[0])
		soup=BeautifulSoup(r.text,'html.parser')
		b=re.findall(r'\[(.*)\]',soup.body.script.string.split(';')[1])
		if 'https:' in re.sub('\"','',eval(re.sub(r'\\','',repr(b[0])))).split(','):
			self.comicDict[soup.title.text.split('-')[1]]=re.sub('\"','',eval(re.sub(r'\\','',repr(b[0])))).split(',')
		else:
			self.comicDict[soup.title.text.split('-')[1]]=['https://img.yaoyaoliao.com/'+x for x in re.sub('\"','',eval(re.sub(r'\\','',repr(b[0])))).split(',')]
		r.close()
	def saveComic(self,part):
		self.l3['text']='正在下载漫画'
		global ff,path
		c=0
		if path=='':
			self.l3['text']=''
			raise messagebox.showerror('ERROR','下载文件路径不能为空')
		os.mkdir(path+'\\'+part[0])
		for pic in part[1]:
			time.sleep(0.5)
			self.progress['value']+=100/(len(part[1])*(ff))
			c+=1
			r=requests.get(pic)
			if pic[-1]=='0':
				f=open(path+'\\'+part[0]+'\\'+str(c)+'.png','wb')
				f.write(r.content)
				r.close()
				f.close()
			f=open(path+'\\'+part[0]+'\\'+str(c)+'.jpg','wb')
			f.write(r.content)
			r.close()
			f.close()
	@staticmethod
	def runthread(func, args):
		global ff,path
		try:
			print(type(args))
			if type(args)==type({}):
				path=filedialog.askdirectory()
				ff=len(args)
				for arg in args.items():
					t=threading.Thread(target=func,args=(arg,))
					t.setDaemon(1)
					t.start()
				self.l3['text']=''
				self.progress['value']=0.0
			elif type(args)==type([]):
				print(111)
				ff=len(args)
				for arg in args:
					t=threading.Thread(target=func,args=(arg,))
					t.setDaemon(1)
					t.start()
				self.l3['text']=''
				self.progress['value']=0.0
			else:
				print(111)
				t=threading.Thread(target=func,args=(args,))
				t.setDaemon(1)
				t.start()
		except:
			pass
manhua=bnComic()
manhua.mainloop()
