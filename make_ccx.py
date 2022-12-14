version='1.0.1'
print('\n南海蒟蒻 ccx简易打包器',version)
print('\n建议在vscode终端里运行\n')

# package_js_list.txt
#	主程序（例如./index.js）必须写在 package_js_list.txt 的第一行！
#	填写在此处的文本文件会以eval的形式放入main.js
#	填写 /* 结尾以表示文件夹下的所有文件。

# package_txt_list.txt
#	可以不写。
#	填写在此处的文本会以返回字符串的形式放入main.js
#	填写 /* 结尾以表示文件夹下的所有文件。

# 运行这个打包机？
#	请先安装python3，然后定位到扩展所在文件夹，
#	再使用命令：
#		python ./make_ccx.py
#	或简写指令（部分系统可能不支持）：
#		py make_ccx.py
#	也可以放置在固定目录，并配置全局环境变量，好处是不会多占空间，也方便更换打包器。

# 该打包器的优点：
#	安装python3后，放入扩展所在文件夹即可使用。
#	只需要填写 info.json 就可以使用，不需要 package.json 。
#	智能识别是需要打包程序（package code to ccx）还是需要将build文件夹压缩。
#		识别方式：如果文件夹里有info.json，那么就打包程序，否则如果build文件夹里有info.json，那么将build文件夹压缩。
#	（仅 package code to ccx 有效）扩展图标仅打包 info.json 里用到的。（即便如此，也不建议使用其它路径作为封面。）
#	（仅 package code to ccx 有效）不需要经过 build 文件夹就能完成打包。
#	不会删除 dist 文件夹里的旧版本ccx。
#	不会吞js里指定的文件路径。
#	更清晰的打包过程输出。
#	极快的打包速度。
#	打包后的 main.js 没有多余的一大堆注释。
#	打包后，扩展在ClipCC加载文件失败时会弹窗提示。（如果是可以被捕捉的错误）
#	扩展内使用函数 require('extension-version') 可以读取版本号。
#	扩展内使用函数 require('extension-id') 可以读取扩展ID。

# 该打包器的缺点：
#	不会在DevTools的源代码中显示该扩展的文件夹。（但你可以通过vm查看扩展源码。报错时只需展开报错信息，然后追踪开头为 VM 的文件。）

buildfile='./build'
exportFolderName='./dist'

#————————————————————————————————
try:
	print('#️⃣  import\n\tjson\n\tzipfile\n\tos')
	import json,zipfile,os
	print('▶ run in',os.getcwd())
	if os.path.exists('./info.json'):
		print('▶ package code to ccx\n🔍 read ./info.json')
		info= json.loads(open('./info.json','r').read())
	else:
		infojsonfile= buildfile + '/info.json'
		if os.path.exists('./build/info.json'):
			#将build直接压缩为ccx
			print('▶ build to ccx\n🔍 read ./build/info.json')
			info= json.loads(open('./build/info.json','r').read())
			print('📦 packaging ',end='')
			zipname= ("%s/%s@%s.ccx" %(exportFolderName, info['id'], info['version']) )
			print(zipname)
			if not os.path.exists(exportFolderName): 
				os.makedirs(exportFolderName)
			if os.path.exists(zipname): 
				os.remove(zipname)
			z= zipfile.ZipFile(zipname,"w", zipfile.ZIP_DEFLATED)
			for dirpath,dirs,files in os.walk(buildfile):
				for f in files:
					p= (os.path.join(dirpath, f)).replace('\\','/')
					arcn= p[len(buildfile)+1:]
					print('\t➕ add %s\n\t    to %s'%(p,arcn))
					z.write(p, arcname= arcn)
			print('\t✅ done\n✅ 打包完成\n')
		else:
			print('\n❌ 打包失败！未能识别到info.json\n')
		exit()


	print('📝 variable cache main.js')
	mainjs= (
'''/*nhjr make_ccx.py %s*/try{var __webpack_modules__={
"clipcc-extension":m=>{m.exports=
\tself.ClipCCExtension
},"extension-version":m=>{m.exports=
\t%s
},"extension-id":m=>{m.exports=
\t%s
}''' %(version, json.dumps(info['version']), json.dumps(info['id'])) )
	print('\t#️⃣  define a function')
	def mainjsadd(i,j,k,l,m):
		global mainjs
		mainjs+= (
''',"%s":%s=>{%s
\t%s
%s}''' %(i,j,k,l,m))

	print('\t🔍 read ./package_js_list.txt')
	if os.path.exists('./package_js_list.txt'):
		with open('./package_js_list.txt','r',encoding='utf-8') as t:
			jsList= t.read().strip()
			if jsList=='':
				print('\n❌ 打包失败！请编写 ./package_js_list.txt\n\tWindows系统运行下方命令使用记事本打开\n\tnotepad ./package_js_list.txt\n')
				exit()
			else:
				jsList= jsList.split('\n')
			main_program= jsList[0].strip()
			for i in jsList:
				j= i.strip()
				if j=='': continue
				if j[-2:]=='/*' or j[-2:]=='\\*':
					for dirpath,dirs,files in os.walk(j[0:-2]):
						for f in files:
							p= (os.path.join(dirpath, f)).replace('\\','/')
							print('\t➕ add js',p)
							with open(p,'r',encoding='utf-8') as txt:
								mainjsadd(p,'(module,exports,require)','eval(',json.dumps(txt.read()),')')
							txt.close()
				else:
					print('\t➕ add js',j)
					with open(j,'r',encoding='utf-8') as txt:
						mainjsadd(j,'(module,exports,require)','eval(',json.dumps(txt.read()),')')
					txt.close()
		t.close()
	else:
		print('\n❌ 打包失败！未识别到 ./package_js_list.txt ，请创建文件并编写。\n\tWindows系统运行下方命令使用记事本打开\n\tnotepad ./package_js_list.txt\n')
		exit()

	print('\t🔍 read ./package_txt_list.txt')
	if os.path.exists('./package_txt_list.txt'):
		with open('./package_txt_list.txt','r',encoding='utf-8') as t:
			jsList= t.read().strip().split('\n')
			if jsList!='':
				for i in jsList:
					j= i.strip()
					if j=='': continue
					if j[-2:]=='/*' or j[-2:]=='\\*':
						for dirpath,dirs,files in os.walk(j[0:-2]):
							for f in files:
								p= (os.path.join(dirpath, f)).replace('\\','/')
								print('\t➕ add txt',p)
								with open(p,'r',encoding='utf-8') as txt:
									mainjsadd(p,'m','m.exports=',json.dumps(txt.read()),'')
					else:
						print('\t➕ add txt',j)
						with open(j,'r',encoding='utf-8') as txt:
							mainjsadd(j,'m','m.exports=',json.dumps(txt.read()),'')
						txt.close()
		t.close()
	mainjs+= (('''
};
var __webpack_module_cache__={};
function __webpack_require__(moduleId){
	var cachedModule=__webpack_module_cache__[moduleId];
	if(cachedModule!==undefined)return cachedModule.exports;
	var module=__webpack_module_cache__[moduleId]={exports:{}};
	__webpack_modules__[moduleId](module,module.exports,__webpack_require__);
	return module.exports
};
var __webpack_exports__=__webpack_require__("%s");
module.exports=__webpack_exports__
''' %(main_program)).replace('\n	','').replace('\n','') #去掉换行符和开头的缩进
+'\n'+ ('''
}catch(e){
	console.error(e);
	window.alert('%s  load error\\n'+e)
}''' %("%s@%s.ccx" %(info['id'], info['version']))).replace('\n	','').replace('\n','') )

	print('\t✅ done\n📦 packaging ',end='')
	if not os.path.exists(exportFolderName): 
		os.makedirs(exportFolderName)
	zipname= ("%s/%s@%s.ccx" %(exportFolderName, info['id'], info['version']) )
	print(zipname)
	if os.path.exists(zipname): 
		os.remove(zipname)
	z= zipfile.ZipFile(zipname,"w", zipfile.ZIP_DEFLATED)
	print('\t➕ add',info['icon'])
	z.write(info['icon'])
	print('\t➕ add',info['inset_icon'])
	z.write(info['inset_icon'])
	for dirpath,dirs,files in os.walk('./locales'):
		for f in files:
			p= (os.path.join(dirpath, f)).replace('\\','/')
			print('\t➕ add',p)
			z.write(p)
	print('\t➕ add ./info.json')
	z.write("./info.json")
	print('\t➕ add mainjs cache\n\t    to main.js')
	z.writestr("main.js",data= mainjs)
	if os.path.exists('./settings.json'):
		print('\t➕ add ./settings.json')
		z.write("./settings.json")

	print('\t✅ done\n✅ 打包完成\n')
except Exception as e:
	print('\n❌ 打包失败！%s\n'%e)