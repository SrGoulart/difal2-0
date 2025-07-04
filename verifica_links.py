import requests
from itertools import product

# Listas de palavras por enigma
enigma1 = ["manual", "guia", "mapa", "manifesto", "roteiro"]
enigma2 = ["carta", "baralho", "taro", "jogo", "ficha"]
enigma3 = ["dourado", "ticket", "codigo", "chave", "segredo"]

# Gera todas as combinações
combinacoes = product(enigma1, enigma2, enigma3)

# Testa os links
for e1, e2, e3 in combinacoes:
    slug = f"{e1}{e2}{e3}"
    url = f"https://bit.ly/{slug}"
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        if response.status_code != 404:
            print(f"✅ POSSÍVEL LINK VÁLIDO: {url} (status {response.status_code})")
    except Exception as e:
        print(f"Erro ao testar {url}: {e}")
