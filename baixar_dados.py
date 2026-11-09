"""Download e validação dos benchmarks públicos da OR-Library."""
from pathlib import Path
from urllib.request import Request,urlopen
import hashlib
from modelo import ler_instancias
BASE='https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/'
ARQUIVOS={'wt40.txt':40,'wt50.txt':50,'wt100.txt':100}

def preparar_dados(destino:Path, modo:str):
    destino.mkdir(exist_ok=True,parents=True)
    if modo=='piloto':
        path=destino/'wt40_primeira_instancia.txt'
        if not path.exists():raise FileNotFoundError('Arquivo do piloto está ausente do pacote.')
        inst=ler_instancias(path,40)
        if len(inst)!=1:raise ValueError('Piloto deve conter 1 instância.')
        return inst,{path.name:hashlib.sha256(path.read_bytes()).hexdigest()}
    inst=[];hashes={}
    for nome,n in ARQUIVOS.items():
        path=destino/nome
        if not path.exists():
            print(f'Baixando dataset oficial {nome} (OR-Library)...',flush=True)
            try:
                req=Request(BASE+nome,headers={'User-Agent':'Mozilla/5.0 research WSM GA reproducibility'})
                with urlopen(req,timeout=45) as resp:conteudo=resp.read()
                if len(conteudo)<1000:raise ValueError('Arquivo recebido muito pequeno.')
                path.write_bytes(conteudo)
            except Exception as exc:
                raise RuntimeError(f'Falha ao baixar {BASE+nome}.\n'
                    f'Baixe manualmente o arquivo para {path} e execute novamente. Erro: {exc}') from exc
        lote=ler_instancias(path,n)
        if len(lote)!=125:
            raise ValueError(f'{nome}: esperado exatamente 125 instâncias, recebidas {len(lote)}.')
        hashes[nome]=hashlib.sha256(path.read_bytes()).hexdigest()
        inst.extend(lote)
    if len(inst)!=375:raise AssertionError('Esperadas 375 instâncias oficiais.')
    return inst,hashes
