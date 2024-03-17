rm tags > /dev/null
ctags --output-format=json --language-force=C --append --recurse -o tags
python /opt/python/analyze.py
