rm tags > /dev/null
[[ ! -z $1 ]] && pwd=$1
pwd=$pwd
ctags --output-format=json --language-force=C --append --recurse -o tags
ls --recursive | grep ":" > dirs
grep -r "#include" > deps
python -i /opt/python/analyze.py
