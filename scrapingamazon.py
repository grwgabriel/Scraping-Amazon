import requests
import re
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver import ActionChains
import traceback
from datetime import date
from unidecode import unidecode

#Inicia o webdriver
servico = Service(ChromeDriverManager().install())
navegador = webdriver.Chrome()

#Abrindo o navegador
navegador.get('https://www.amazon.com.br/ref=nav_logo')
navegador.implicitly_wait(5)

#Fazendo a pesquisa
navegador.find_element(By.ID,'twotabsearchtextbox').send_keys('Livro', Keys.ENTER)
navegador.implicitly_wait(5)

#Localizando elementos
lista_celular = navegador.find_elements(By.CLASS_NAME,'sg-col-4-of-24')
abas = navegador.find_elements(By.CLASS_NAME,'s-pagination-item')
numeros_abas = []

#Verificando a quantidade de abas existente
for aba in abas:
    texto = aba.text
    if texto.isdigit():
        numero = int(texto)
        numeros_abas.append(numero)
abas_total = max(numeros_abas)

navegador.implicitly_wait(10)
proxima_aba = navegador.find_elements(By.CLASS_NAME,'s-pagination-item')

#Declarando as listas
Titulo = [] 
Preco_original = [] 
Preco_Atual = [] 
Avaliacao = []  
Link = []
Data = []

#Iterando sobre as abas
for _ in range(abas_total-1):
    lista_celular = navegador.find_elements(By.CLASS_NAME,'sg-col-4-of-24')

    #Iterando sobre os itens
    for celular in lista_celular:
        try:
            #Verificando se é um item iterável
            item = celular.get_attribute('data-asin')
            if item != None:
                navegador.implicitly_wait(2)
                
                #Raspando os dados
                titulo = celular.find_element(By.CLASS_NAME,'a-size-base-plus').text
                preco_A = celular.find_element(By.CLASS_NAME,'a-price-whole').text
                listaprecosoriginais = celular.find_element(By.CSS_SELECTOR, "span.a-price.a-text-price")
                verifica = listaprecosoriginais.get_attribute('data-a-strike')
                if verifica != None:
                    lista = listaprecosoriginais.find_elements(By.TAG_NAME,'span')
                    for preco in lista:
                        Preco_or = re.sub(r'\bR\$','',preco.text)
                else:
                    Preco_or = None
                
                avaliacao = celular.find_element(By.CLASS_NAME,'a-icon-alt').get_attribute('outerHTML')
                regexavaliacao = re.search(r'(\d,\d)',avaliacao).group(1)
                links = celular.find_elements(By.TAG_NAME,'a')
                for link in links:
                    linkitem = link.get_attribute('href')
                titulo_corrigido = unidecode(titulo)
                preco_corrigido = unidecode(preco_A)

                #Insere nas listas
                Titulo.append(titulo_corrigido)
                Preco_original.append(Preco_or)
                Preco_Atual.append(preco_corrigido)
                Avaliacao.append(regexavaliacao)
                Link.append(linkitem)
                Data.append(date.today())

                print(titulo_corrigido,preco_corrigido,Preco_or,regexavaliacao,linkitem)
        except: print('nao encontrou')
    proxima_aba_atualizada = []
    for aba in proxima_aba:
        botao_aba = aba.get_attribute('aria-label')
        if botao_aba is not None and 'próxima' in botao_aba:
            aba.click()
            break
        else:
            proxima_aba_atualizada.append(aba)
    proxima_aba = navegador.find_elements(By.CLASS_NAME, 's-pagination-item')

    #Criação do dataframe
dictDF = {'Titulo': Titulo,
            'Preço Original': Preco_original,
            'Preço Atual': Preco_Atual,
            'Avaliação': Avaliacao,
            'Link':Link,
            'Data': Data}
df = pd.DataFrame(dictDF)
print(df)

#Exportação para excel
data_arquivo = date.today().strftime("%Y-%m-%d")
df.to_excel(f'Scraping_Amazon_{data_arquivo}',index=False, engine='xlsxwriter')



