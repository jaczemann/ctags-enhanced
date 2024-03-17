import re
import ast

true = True


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
	print(tgs)

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
			print(tags_proc[tags.index(tag)]['typeref'])
			tags_proc[tags.index(tag)].update({'typeref': tags_proc[tags.index(tag)]['typeref'].split(":")[1]})

	if (tag['kind'] == 'variable'):
		txt = tag['typeref']
		if ':' in tags_proc[tags.index(tag)]['typeref']:
			print(tags_proc[tags.index(tag)]['typeref'])
			tags_proc[tags.index(tag)].update({'typeref': tags_proc[tags.index(tag)]['typeref'].split(":")[1]})

	if (tag['kind'] == 'enumerator'):
		parent = [x for x in tags if x['name'] == tag['scope']][0]

		if (type(tags_proc[tags.index(parent)]['pattern']) == type("")):
			tags_proc[tags.index(parent)].pop('pattern')
			tags_proc[tags.index(parent)]['pattern'] = list()

		tags_proc[tags.index(parent)]['pattern'].append(tag['pattern'].replace("/^\t", "").replace("$/", "").replace(",", ""))

print(tags_proc)

tags_group = {"files": []}
file_struct = { "variables":[], "functions":[], "types": [], "enums": [] }


source_files = list(set([tag['path'] for tag in tags_proc]))

for src in source_files:
	tags_group['files'].append(dict({src: file_struct}))

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
