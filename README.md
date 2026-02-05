# TJPA Scraper

Este projeto traz a implementação de um scraper para o portal de consultas do **Tribunal de Justiça do Estado do Pará**.

# Sobre a fonte

## Descrição da fonte

Ao acessar o link disponibilizado para consulta: https://consulta-processual-unificada-prd.tjpa.jus.br/#/consulta, evidencia-se uma consulta que, no primeiro momento, aparenta ser complexa dada a presença de um captcha, porém a mesma é realizada com o preenchimento de somente um campo de busca.

A fonte permite a consulta através de diversas entradas diferentes, como o número do processo, CPF da parte, CNPJ da parte, Nome da parte, Número do Inquerito Policial e Número da OAB. Ao realizar a busca, podemos ter os seguintes retornos visuais:

* Uma lista de nomes (é o retorno padrão para a busca pelo nome da parte). Ao selecionar um dos nomes retornado, é exibida a lista de processos para aquele nome.
* Uma lista de processos diretamente.

Estando na listagem de processos, o usuário pode selecionar um dos items para a visualização dos dados.

Ao visualizar um processo, temos acesso às informações do processo, como Número do processo, Partes, Classe, Assunto, Valor da causa, Movimentações, Documentos.

## Dificuldades técnicas encontradas

No primeiro momento, avaliei o html da página para entender como fazer a extração das informações, porém pude observar que a página utilizava um html gerado através de um script.js, o que fazia com que ele não fosse carregado diretamente ao requisitar a url. 

Dado isto, decidi partir para a abordagem de avaliar as requisições feitas pela página para entender o fluxo de transferência de dados realizada e pude encontrar as requisições feitas para a API de consulta dos processos. 

Durante a análise, também observei que o captcha presente na primeira página não afetava nenhuma das requisições feitas para a API, o que me permitia não resolver ele e partir diretamente para as consultas. 

Já no momento das consultas, me deparei com retornos diferentes para tipos diferentes de entradas na busca, o que me fez ter que validar entrada por entrada para garantir consistência das consultas.

Além dos pontos acima, em consultas paginadas, a fonte não se comportou de forma consistente com os dados informados por ela mesmo, o que me forçou a fazer um mecanismo mais independente para obter as informações paginadas.

# Sobre a solução

## Estratégia de extração

A estratégia de extração adotada na solução foi **requisições HTTP**, através de endpoints da API capturados enquanto analisava a aplicação.

Em um dos script.js contidos na página, pude encontrar as rotas e sub-rotas necessárias para realizar a extração das informações.

A entrada na consulta tem seu tipo identificado através de Expressões Regulares (Regex) definidos dentro do script.js. Para cada tipo de entrada identificado, temos uma sub-rota específica para realização da consulta dos processos. 

Como a solução faz as consultas diretas aos endpoints, tive que incorporar as Expressões Regulares diretamente na solução, para realizar o roteamento corretamente.

Para a obtenção das movimentações de um processo, temos somente uma única rota, que utiliza algumas das informações obtidas inicialmente na consulta do processo.

Para garantir consistência nas consultas e dados, foram implementadas algumas tratativas:

* Caso não seja possível obter as informações de movimentações de um processo, o processo será exportado sem movimentações.
* Tanto nas buscas de processos, quanto nas buscas de movimentações, foi implementado um mecanismo para deduplicação dos resultados. Esse mecanismo foi implementado pois a fonte, durante a paginação, retornava o mesmo elemento em páginas diferentes.

## Resultados obtidos

Após a implementação da solução, foi obtido um sistema que consulta os processos diretamente do sistema de Consulta Unificada de Processos do TJPA, trata algumas das informações, obtem todas as movimentações para cada processo e exporta cada processo individualmente no formato CSV (com algumas formatações nos nomes das variavéis para uma melhor visualização do usuário) e no formato JSON (utilizando os nomes de variavéis iguais aos que foram extraidos).

### Como executar:

Para executar a solução, pode ser feito de duas formas, as quais irei descrever a seguir.

Padrões da entrada para busca:
* CPF - "12345678909" ou "123.456.789-09"
* CNPJ - "123456789000123" ou "12.456.789/0001-23" 
* CNJ - "00025935220188140051" ou "0002593-52.2018.8.14.0051"
* Nome Parte - Nome e sobrenome. Ex: Maria Silva
* Nome Exato - Nome e sobrenome entre aspas duplas. Ex: "Maria Silva"
* OAB - 'oab:' ou 'oab' seguido do número + UF. Ex: "OAB:12345BA", "oab123456ba" ou "OAB123457ba"
* Inquerito policial - 'inq:' seguido do número do inquerito policial. Ex: "inq:12345"

1. Utilizando Docker:
    -
    O projeto possui um arquivo docker-compose, que já contém toda a configuração necessária para rodar, mesmo que não possua o Python instalado. É necessário ter o Docker instalado. Pode baixa-lo [aqui](https://www.docker.com/get-started/).

    Estando no diretório do projeto, utilize o seguinte comando para executa-lo:
    ```docker
    docker compose run scraper python main.py args
    ```
    
    sendo *args* a busca processual a ser realizada.

2. Utilizando Python diretamente:
    -

    O projeto foi implementado na versão 3.12.2 do python.

    Para executar o projeto utilizando Python diretamente, é necessário instalar as bibliotecas requeridas pelo projeto. Recomendo a utilização de um ambiente virtual antes de prosseguir. O ambiente virtual pode ser criado a partir ds comandos a seguir (Caso não queira utilizar um ambiente virtual, pode pular para a próxima etapa):
    ```python
    python -m venv venv
    source venv/bin/activate
    ```
    Para instalar as bibliotecas necessárias, utilize o seguinte comando:
    ```python
    pip install -r requeriments.txt
    ```

    Assim que todas as bibliotecas estiverem instaladas, pode executar o projeto a partir do comando:
    ```python
    python main.py
    ```

    Ao executar, será solicitado a busca processual a ser realizada.

### Saída:

Após executar o projeto, independente da forma escolhida, teremos alguns outputs.

1. Data
    -
    Caso a busca seja realizada com sucesso e processos sejam localizador, no diretório `data\` poderá ser encontrado mais dois diretórios, o `csv_exports` e o `json_exports`, cada um desses armazenando a exportação de cada processo encontrado no seu devido formato indicado.
2. Logs
    -
    Em todas as execuções do projeto, sejam sucesso ou falhas, teremos um arquivo de log gerado relativo à execução.

## Possíveis melhorias

* Implementar um sistema mais robusto de requisições, permitindo um paralelismo sem comprometer o RateLimit da fonte.
* Incrementar o que é exportado nos logs, para um melhor entendimento e facilitar a análise de problemas a partir deles.
* Realizar a coleta dos documentos do processo.

## Testes

O projeto conta com testes unitários, garantindo o funcionamento do scraper implementado.

Para executar os testes, utilizaremos a biblioteca `pytest`. Se já instalou as bibliotecas necessárias através do arquivo `requirements.txt`, ela já estará instalada corretamente.

Utilize o comando a seguir para executar os testes:

Em python:
```python
python -m pytest
```

ou, utilizando o docker:
```docker
docker compose run scraper python -m pytest
```