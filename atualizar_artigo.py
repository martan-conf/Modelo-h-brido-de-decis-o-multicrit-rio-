"""Insere automaticamente as tabelas e figuras produzidas pelo experimento.

USO (após executar.py):
    python atualizar_artigo.py --modo completo
O documento ainda requer revisão humana da discussão e das conclusões.
"""
from pathlib import Path
import argparse,csv
from docx import Document
from docx.shared import Cm,Pt
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parent.parent

def csv_ler(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def inserir_tabela(doc,par,head,linhas):
    tabela=doc.add_table(rows=1,cols=len(head));tabela.style='Table Grid';tabela.alignment=WD_TABLE_ALIGNMENT.CENTER
    for j,v in enumerate(head):tabela.rows[0].cells[j].text=str(v)
    for linha in linhas:
        cells=tabela.add_row().cells
        for j,v in enumerate(linha):cells[j].text=str(v)
    for k,row in enumerate(tabela.rows):
        for cell in row.cells:
            for pp in cell.paragraphs:
                pp.paragraph_format.first_line_indent=Cm(0);pp.paragraph_format.line_spacing=1
                pp.paragraph_format.space_after=Pt(1)
                for run in pp.runs:
                    run.font.name='Times New Roman';run.font.size=Pt(8 if len(head)>=6 else 9)
                    if k==0:run.bold=True
    par._p.addnext(tabela._tbl)
    par._element.getparent().remove(par._element)

def popular(modo):
    base=ROOT/'codigo'/'resultados'/modo
    artigo=ROOT/'artigo'/'Artigo_Modelo_MCDM_WSM_AG_ABNT_MODELO.docx'
    if not artigo.exists():raise FileNotFoundError(artigo)
    t1=csv_ler(base/'TABELA_1_COMPARACAO_METODOS.csv')
    t2=csv_ler(base/'TABELA_2_GANHO_HIBRIDO.csv')
    t3=csv_ler(base/'TABELA_3_SENSIBILIDADE.csv')
    t4=csv_ler(base/'TABELA_4_TESTE_SINAIS.csv')
    if not t3:raise ValueError('Falta a sensibilidade. Execute sem --sem-sensibilidade.')
    d=Document(artigo)
    selecionados={'EDD','SPT','WSPT','WSM_Equilibrado','AG','WSM_AG'}
    ts={
       'TABELA_1':(['N','Método','Instâncias','Média Z','DP entre instâncias','Tempo médio (s)'],[
           [x['n'],x['metodo'],x['instancias'],x['media_atraso_ponderado'],x['dp_entre_instancias'],x['media_tempo_s']]
           for x in t1 if x['metodo'] in selecionados]),
       'TABELA_2':(['N','Instâncias','Δ médio (AG − híbrido)','Melhorou','Empatou','Piorou'],[
           [x['n'],x['instancias'],x['media_delta_ag_menos_hibrido'],x['melhorou'],x['igual'],x['piorou']]
           for x in t2]),
       'TABELA_3':(['N','Cenários','Tau médio','Primeiro igual (%)','Top 5 comum','Atraso médio'],[
           [x['n'],x['cenarios_peso_por_instancia'],x['tau_medio'],
           round(100*float(x['proporcao_primeiro_igual']),1),x['top5_intersecao_medio'],x['atraso_medio']]
           for x in t3]),
       'TABELA_4':(['N','Instâncias','Ganhos','Empates','Perdas','p (Holm)'],[
           [x['n'],x['instancias'],x['ganhos'],x['empates'],x['perdas'],x['p_holm']] for x in t4]),
    }
    substituidos=[]
    for par in list(d.paragraphs):
        for codigo,(head,linhas) in ts.items():
            if f'[[{codigo}]]' in par.text:
                inserir_tabela(d,par,head,linhas);substituidos.append(codigo);break
        else:
            for j in range(1,5):
                chave=f'FIGURA_{j}'
                if f'[[{chave}]]' in par.text:
                    arq=base/(f'FIGURA_{j}_'+('COMPARACAO' if j==1 else 'GANHO_HIBRIDO' if j==2 else 'CONVERGENCIA' if j==3 else 'SENSIBILIDADE')+'.png')
                    if not arq.exists():raise FileNotFoundError(arq)
                    par.clear();par.alignment=WD_ALIGN_PARAGRAPH.CENTER
                    par.paragraph_format.first_line_indent=Cm(0)
                    par.add_run().add_picture(str(arq),width=Cm(15.2))
                    substituidos.append(chave)
                    break
    esperados=set(ts)|{f'FIGURA_{j}' for j in range(1,5)}
    if set(substituidos)!=esperados:raise RuntimeError(f'Marcadores incompletos: {esperados-set(substituidos)}')
    destino=ROOT/'artigo'/f'Artigo_Modelo_MCDM_WSM_AG_RESULTADOS_{modo.upper()}.docx'
    if modo=='piloto':
        d.paragraphs[1].insert_paragraph_before('DOCUMENTO DE VALIDAÇÃO DO SOFTWARE — APENAS 1 INSTÂNCIA: NÃO USAR COMO RESULTADO DO ARTIGO COMPLETO.')
    d.save(destino)
    print('Artigo com tabelas e figuras inseridas:',destino)
    print('IMPORTANTE: ainda é necessário interpretar os resultados, revisar resumo e redigir a conclusão.')
    return destino

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--modo',choices=['completo','piloto'],default='completo')
    args=parser.parse_args();popular(args.modo)
