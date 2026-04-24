import urllib.request

gids = [0, 1, 2, 342288397, 977039644, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010]
sheet_id = "1iGj4-vknwzepbrHdRz1PwisZU2foU7aW"

for gid in gids:
    try:
        url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req).read().decode('utf-8')
        first_line = data.split('\n')[0]
        lines = [l for l in data.split('\n') if l.strip()]
        cols = first_line.split(',')
        
        print(f"GID {gid}: {len(cols)} colunas, {len(lines)} linhas - {first_line[:80]}...")
    except Exception as e:
        pass
