import re
import ast
import os
from collections import defaultdict




#TODO: Types diagram
#TODO: ADD TYPE option
#TODO: DISPLAY TYPE option
#TODO: Interface diagram
#TODO: ADD INTERFACE option
#TODO: DISPLAY INTERFACE option



true = True

def createPathNavigation():
	navig=[]
	for root, dirs, files in os.walk(os.getcwd()):
		navig.append([root.replace(r'/opt', ''), dirs])

	return navig

navig = createPathNavigation()

def createListOfModulesInPackageTree():
	tree_of_modules=[]
	for root,dirs,files in os.walk(os.getcwd()):
		tree_of_modules.append([root, [file for file in files if '.c' in file]])
	return tree_of_modules

tree_of_modules = createListOfModulesInPackageTree()

with open("deps", "r") as deps_file:
	dps = deps_file.readlines()
	for i, line in enumerate(dps):
		if "#include" not in line:
			dps[i] = ' '
			continue
		dps[i] = dps[i].replace('\n', '')
		dps[i] = dps[i].split(":")
		dps[i][1] = dps[i][1].split(" ")[1]

	files=[]
	for i in dps:
		files.append(i[0])
	set(files)
	deps = {file: [] for file in files}

	for dependency in dps:
		deps[dependency[0]].append(dependency[1])


#TODO: process deps


with open("tags", "r") as tags_file:
	tgs = tags_file.readlines()
	for i, line in enumerate(tgs):
		if 'ptag' in line:
			tgs[i] = ' '
			continue
		tgs[i] = tgs[i].replace('\n', '')
		tgs[i] += ', '
	tgs = ''.join(tgs)
	tgs = tgs.replace("true", "True").replace("false", "False")
	tgs = "[" + str(tgs) + "]"
	tgs = tgs.replace('}, ]', '} ]')

	tags = ast.literal_eval(tgs)


tags_proc = list(tags)

for tag in tags:
	#tags_proc[tags.index(tag)].pop('_type')
	#tags_proc[tags.index(tag)].pop('file')

	if (tag['kind'] == 'function'):
		txt = tag['pattern']
		tags_proc[tags.index(tag)]['pattern'] = re.findall(r'\((.*?)\)',txt)[0].split(",")
		for i in range(0, len(tags_proc[tags.index(tag)]['pattern'])):
			tags_proc[tags.index(tag)]['pattern'][i] = tags_proc[tags.index(tag)]['pattern'][i].replace(' *', '*')
			if tags_proc[tags.index(tag)]['pattern'][i]:
				if " " in tags_proc[tags.index(tag)]['pattern'][i]:
					pattern = tags_proc[tags.index(tag)]['pattern'][i].split(" ")
					tags_proc[tags.index(tag)]['pattern'][i] = {"arg_typeref": ' '.join(pattern[:-1]), "arg_name": pattern[-1]}
				else:
					pattern = tags_proc[tags.index(tag)]['pattern'][i]
					tags_proc[tags.index(tag)]['pattern'][i] = {"arg_name": pattern[-1]}


		if ':' in tags_proc[tags.index(tag)]['typeref']:
			tags_proc[tags.index(tag)].update({'typeref': tags_proc[tags.index(tag)]['typeref'].split(":")[1]})

	if (tag['kind'] == 'variable'):
		txt = tag['typeref']
		if ':' in tags_proc[tags.index(tag)]['typeref']:
			tags_proc[tags.index(tag)].update({'typeref': tags_proc[tags.index(tag)]['typeref'].split(":")[1]})

	if (tag['kind'] == 'enumerator'):
		parent = [x for x in tags if x['name'] == tag['scope']][0]

		if (type(tags_proc[tags.index(parent)]['pattern']) == type("")):
			tags_proc[tags.index(parent)].pop('pattern')
			tags_proc[tags.index(parent)]['pattern'] = list()

		tags_proc[tags.index(parent)]['pattern'].append(tag['pattern'].replace("/^\t", "").replace("$/", "").replace(",", ""))


tags_group = {"files": []}
file_struct = { "variables":[], "functions":[], "types": [], "enums": [] }


source_files = list(set([tag['path'] for tag in tags_proc]))
if "blueprint" in source_files: source_files.remove("blueprint")
if "tags" in source_files: source_files.remove("tags")
if "deps" in source_files: source_files.remove("deps")

tags_group['files']={key: file_struct for key in source_files}

for src in source_files:
	#tags_group['files'].append(dict({src: file_struct})) #FIXME
	#tags_group['files'].append({src: file_struct})

	for tag in tags_proc:
		if tag['path'] == src:
			if tag['kind'] == 'variable':
				tags_group['files'][src]['variables'].append(tag)
			if tag['kind'] == 'function':
				tags_group['files'][src]['functions'].append(tag)
			if tag['kind'] == 'typedef':
				tags_group['files'][src]['types'].append(tag)
			if tag['kind'] == 'enum':
				tags_group['files'][src]['enums'].append(tag)

print("\n\n\n")
print(tags_group)



def createBlueprint():
	with open("blueprint", "w") as blueprint:
		blueprint.write("BEGIN\n")

	bp_data = []

	bp_data.append("NEW\tPACKAGE\t" + navig[0][0].split(r'/')[-1] + ";0\n")
	#for path, create in navig:
		#bp_data.append("NEW\tPACKAGE\t" + path + "\t" + ';'.join(create) + "\n")

	i=0
	d=0
	for pckg, to_create in navig:
		bp_data.append("GOTO\tPACKAGE\t" + pckg.split(r'/')[-1] + ';' + str(i) + '\n')
		if pckg.split(r'/')[-1] == "core":
			bp_data.append("NEW\tDIAGRAM\t" + navig[0][0].split(r'/')[-1] + ' MCD' + ';' + str(d) + '\n')
			bp_data.append("GOTO\tDIAGRAM\t" + navig[0][0].split(r'/')[-1] + ' MCD' + ';' + str(d) + '\n')
			bp_data.append("NEW\tBSW\t" + navig[0][0].split(r'/')[-1] + '\n')

			for pckg, modules in tree_of_modules:
				if navig[0][0].split(r'/')[-1] in pckg:
					for module in modules:
						bp_data.append("NEW\tMODULE\t" + module + '\n')
						src=[file for file in source_files if module in file][0]
						for variable in tags_group['files'][src]['variables']:
							bp_data.append("NEW\tATTRIBUTE\t" + variable['name'] + '\t' + variable['typeref'] + '\n')
						for function in tags_group['files'][src]['functions']:
							bp_data.append("NEW\tOPERATION\t" + function['name'] + '\t' + function['typeref'] + '\n')

							for param in function['pattern']:
								if(param == ""):
									continue
								bp_data.append("NEW\tARGUMENT\t" + param['arg_name'] + '\t' + param['arg_typeref'] + '\n')
								print(str(type(param))+str(param))


						bp_data.append("NEW\tREALISATION\n")
						bp_data.append("DISPLAY\tMODULE\n")
			d+=1
		i_backup = i
		for create in to_create:
			i+=1
			bp_data.append("NEW\tPACKAGE\t" + create + ';' + str(i) + '\n')
		i = i_backup
		i += 1




	bp_data.append("END\n")
	with open("blueprint", "a") as blueprint:
		blueprint.writelines(bp_data)

createBlueprint()
