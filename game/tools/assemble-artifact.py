# Assemble the single-file artifact: the pre-boot stadium layer (and its CSS) must come
# BEFORE the 10 MB inline game script, so it is painted from the first bytes.
import re, sys
S = sys.argv[1] if len(sys.argv) > 1 else '.'
s = open('dist-single/index.html').read()
h = re.search(r'<head>(.*?)</head>', s, re.S).group(1)
b = re.search(r'<body[^>]*>(.*)</body>', s, re.S).group(1)
pre = re.search(r'<div id="preboot".*?(?=<div id="app">)', b, re.S).group(0)
b = b.replace(pre, '')
style = re.search(r'<style>html,body.*?</style>', h, re.S).group(0)
h = h.replace(style, '')
metas = ''.join(re.findall(r'<meta[^>]*>|<title>.*?</title>', h))
h_rest = re.sub(r'<meta[^>]*>|<title>.*?</title>', '', h)
page = metas + style + pre + h_rest + b
open(S + '/golden-rally.html', 'w').write(page)
import os; os.makedirs(S + '/pub', exist_ok=True); open(S + '/pub/index.html', 'w').write('<!doctype html><html lang="fr"><head>' + metas + style + '</head><body>' + pre + h_rest + b + '</body></html>')
print('preboot offset', page.index('id="preboot"'), 'script offset', page.index('<script'), 'size', len(page))
