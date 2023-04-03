
# from cProfile import run
# from distutils.log import debug
import os
import glob
import pandas as pd
import tabula

from os import walk
from flask import Flask, render_template, request, send_file
# from werkzeug.utils import secure_filename
from waitress import serve


app = Flask(__name__)

mododebug = True

# obtém o caminho absoluto do diretório atual
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))  # c:\Users\NTIC\Desktop\Desenvolvimento\Python\pdfToCsv\app


# constrói o caminho para o diretório onde deseja salvar o arquivo
# diretorio_saida = os.path.join(diretorio_atual, 'pdfToCsv/app/Saida/')


DIRETORIO_SAIDA = DIRETORIO_ATUAL + '/Saida/'


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        removeArquivosSaida()

        files = request.files.getlist('pdf_files')
        # file_paths = []
        for file in files:
            file_path = os.path.join(DIRETORIO_SAIDA, file.filename)
            file.save(file_path)
            # file_paths.append(file_path)
        pdfToCsv()
        filesDownload = carregaAquivosDownload()
        return render_template('arquivos.html', file_paths=filesDownload)
    else:
        filesDownload = carregaAquivosDownload()
        return render_template('arquivos.html', file_paths=filesDownload)


def carregaAquivosDownload():
    file_paths = []
    path = DIRETORIO_SAIDA
    print(path)
    for (dirpath, dirnames, filenames) in walk(path):
        file_paths.extend(filenames)
        break
    return file_paths


@app.route('/download/<filename>')
def download(filename):  # In your case fname is your filename
    try:
        path = os.path.join(DIRETORIO_SAIDA, filename)
        return send_file(path, mimetype='text/csv', as_attachment=True)
    except Exception as e:
        return str(e)


def pdfToCsv():
    arquivos = os.listdir(DIRETORIO_SAIDA)

    dfDadosFinal = pd.DataFrame()

    for arquivo in arquivos:

        if os.path.isfile(os.path.join(DIRETORIO_SAIDA, arquivo)):
            lista_tabelas = tabula.read_pdf(DIRETORIO_SAIDA + arquivo, pages="all", lattice=True, encoding='utf-8')

            dfDadosPdf = pd.DataFrame()

            for tabela in lista_tabelas:
                lista = tabela.columns.tolist()
                if len(lista) > 2:
                    lista[1] = lista[1].replace(",", ";")
                    lista[1] = lista[1].replace("\r", " ")
                    partes = str(lista).split(', ')

                    lista = [partes[0], partes[1], partes[2]]

                    s = lista[0]
                    numeros = ''
                    for c in s:
                        if c.isdigit():
                            numeros += c

                    dividindoDenominacao = partes[1].split('; ')
                    denominacao = dividindoDenominacao[0]
                    descricaoDoBem = ""
                    if len(dividindoDenominacao) > 1:
                        descricaoDoBem = "".join(dividindoDenominacao[1:])

                    df = pd.DataFrame(lista)
                    df['Numero'] = 1
                    df['Tombamento'] = numeros
                    df['Denominacao'] = denominacao
                    df['Descricao do Bem'] = descricaoDoBem
                    df = df.drop(columns=[0])

                    dfDadosPdf = pd.concat([dfDadosPdf, df], ignore_index=True)

            dfDadosPdf.drop_duplicates(
                subset='Tombamento', keep='first', inplace=True)

            dfDadosPdf.drop(dfDadosPdf[(dfDadosPdf['Denominacao'] == "'EM USO'") |
                                       (dfDadosPdf['Denominacao'] == "'Total Grupo:'") |
                                       (dfDadosPdf['Denominacao'] == "'Unnamed: 0'") |
                                       (dfDadosPdf['Denominacao'] == "'RECOLHIDO'")].index, inplace=True)

            dfDadosFinal = pd.concat([dfDadosFinal, dfDadosPdf], ignore_index=True)

    dfDadosFinal['Numero'] = range(1, len(dfDadosFinal)+1)

    gerarCSV(dfDadosFinal)

    return



def removeArquivosSaida():
    files = glob.glob(DIRETORIO_SAIDA + '*')
    for f in files:
        os.remove(f)
    return True


def gerarCSV(dfDadosFinal):
    ## Criação dos CSV  - START ##

    # Cria arquivo com Patrimônios
    dfDadosFinal.to_csv(DIRETORIO_SAIDA + "Lista Patrimônial" + ".csv", index=False, encoding='utf-8')

    ## Criação dos CSV  - END ##
    return True


if __name__ == '__main__':
    if mododebug:
        # Rodar modo Debug
        app.run(debug=True)
    else:
        # Executar modo produção
        print("Escutando na porta 5000")
        serve(app, host="0.0.0.0", port=5000)
