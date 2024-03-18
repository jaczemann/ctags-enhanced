import re
import ast
import os
from collections import defaultdict

true = True

def createPathNavigation():
	navig=[]
	for root, dirs, files in os.walk(os.getcwd()):
		navig.append([root.replace(r'/opt', ''), dirs])

	return navig

navig = createPathNavigation()



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

for src in source_files:
	#tags_group['files'].append(dict({src: file_struct})) #FIXME
	tags_group['files'].append({src: file_struct})

	for tag in tags_proc:
		if tag['path'] == src:
			if tag['kind'] == 'variable':
				tags_group['files'][source_files.index(src)][src]['variables'].append(tag)
			if tag['kind'] == 'function':
				tags_group['files'][source_files.index(src)][src]['functions'].append(tag)
			if tag['kind'] == 'typedef':
				tags_group['files'][source_files.index(src)][src]['types'].append(tag)
			if tag['kind'] == 'enum':
				tags_group['files'][source_files.index(src)][src]['enums'].append(tag)

print("\n\n\n")
print(tags_group)



def createBlueprint():
	with open("blueprint", "w") as blueprint:
		blueprint.write("BEGIN\n")

	bp_data = []

	bp_data.append("NEW\tROOT\t" + "RootName" + "\n")
	for path, create in navig:
		bp_data.append("NEW\tPACKAGE\t" + path + "\t" + ';'.join(create) + "\n")

	bp_data.append("NEW\tDIAGRAM\tDiagramName\n")
	bp_data.append("GOTO\tDIAGRAM\tDiagramName\n")

	for file in source_files:
		bp_data.append("NEW\tMODULE\t" + file.replace('.c', '') + "\n")


	bp_data.append("END\n")
	with open("blueprint", "a") as blueprint:
		blueprint.writelines(bp_data)

createBlueprint()
