# AgroSmart - Monitoramento Inteligente da Lavoura

Projeto desenvolvido para a **Global Solution 2026 - 1º Semestre - FIAP**.

O AgroSmart é um programa em Python que simula a integração com sensores
Arduino (umidade, temperatura e luminosidade) instalados em diferentes
setores de uma plantação. A partir dessas leituras o sistema mantém um
pequeno banco de dados local, analisa as condições ambientais, calcula o
risco de desperdício de água e gera recomendações de irrigação para o
agricultor, estimando ainda a economia de água em litros e em reais.

## Problema

A agricultura é uma das atividades que mais consome água no mundo. Muitas
propriedades ainda irrigam toda a área da plantação no mesmo horário, sem
levar em conta a umidade real do solo, a temperatura ou a luminosidade. Esse
tipo de irrigação "padrão" causa grandes desperdícios, eleva o custo da
produção e contribui para a escassez hídrica em regiões críticas.

## Objetivo

Oferecer ao pequeno e médio agricultor uma ferramenta simples para:

- Acompanhar em tempo real as condições de cada setor da plantação.
- Saber, com base em regras claras, **se deve ou não irrigar** cada setor.
- Visualizar a economia estimada ao usar irrigação inteligente em vez de
  irrigar tudo por padrão.
- Aprender, por meio de explicações educativas, o impacto de cada variável
  ambiental no consumo de água.

## Funcionalidades

- Cadastro do agricultor.
- Cadastro da propriedade (área em hectares, cultura e nº de setores).
- Coleta de dados ambientais — automática (mock dos sensores Arduino) ou
  manual (digitar os valores).
- Análise de umidade e temperatura, classificando cada setor como
  `IDEAL`, `BAIXA` ou `ALTA`.
- Cálculo do risco de desperdício (0 a 100%).
- Recomendações de irrigação por setor:
  `IRRIGAR URGENTE`, `IRRIGAR MODERADAMENTE`, `MONITORAR` ou `NAO IRRIGAR`.
- Estimativa de economia de água em litros e em reais.
- Histórico das últimas leituras dos sensores.
- Explicações educativas sobre umidade, temperatura, luminosidade e o
  funcionamento do sistema.
- Logs de execução em arquivo (`logs/agrosmart.log`).
- Persistência em JSON (`dados/banco.json`) — os dados permanecem entre
  execuções, funcionando como um banco de dados simples.

## Tecnologias utilizadas

O projeto utiliza somente bibliotecas padrão do Python — não há dependências
externas.

- **Python 3.9+**
- `json` – persistência do banco em arquivo
- `logging` – geração de logs
- `random` – simulação dos sensores Arduino
- `datetime` – data/hora das leituras
- `os` / `sys` – manipulação de pastas e finalização do programa

## Estrutura do projeto

```
1SEM/
├── main.py              # Programa principal (único arquivo de código)
├── README.md            # Este arquivo
├── dados/
│   └── banco.json       # "Banco de dados" gerado em tempo de execução
└── logs/
    └── agrosmart.log    # Logs de execução
```

As pastas `dados/` e `logs/` são criadas automaticamente na primeira execução
caso ainda não existam.

## Como executar

### Pré-requisitos

- Python 3.9 ou superior instalado.

### Passos

1. Clonar o repositório:

```bash
git clone https://github.com/<usuario>/<repositorio>.git
cd <repositorio>
```

2. (Opcional) Criar e ativar um ambiente virtual:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. Executar o programa:

```bash
python main.py
```

Não é necessário instalar dependências (`requirements.txt` não é necessário
porque o projeto usa apenas a biblioteca padrão).

## Fluxo de uso

O programa apresenta um menu interativo. Para uma demonstração completa,
siga a ordem abaixo:

1. **Cadastrar agricultor** – nome, idade e cidade.
2. **Cadastrar propriedade** – nome, área (ha), cultura e número de setores.
3. **Coletar dados ambientais** – opção `1` para coleta automática
   (simulação Arduino) ou `2` para digitar os valores manualmente.
4. **Analisar umidade e temperatura** – mostra a classificação de cada setor.
5. **Exibir recomendações de irrigação** – exibe risco de desperdício e a
   ação recomendada por setor.
6. **Calcular economia estimada** – compara o consumo tradicional com o
   consumo usando o AgroSmart.
7. **Mostrar histórico de leituras** – tabela com os últimos registros.
8. **Explicações educativas** – textos curtos sobre o tema.

## Exemplo de execução

```
============================================================
 AGROSMART - Monitoramento Inteligente da Lavoura
============================================================
 Agricultor:  Joao da Silva
 Propriedade: Fazenda Boa Vista | 10.0 ha | soja
============================================================
  1 - Cadastrar agricultor
  2 - Cadastrar propriedade
  3 - Coletar dados ambientais (Arduino)
  4 - Analisar umidade e temperatura
  5 - Exibir recomendacoes de irrigacao
  6 - Calcular economia estimada
  7 - Mostrar historico de leituras
  8 - Explicacoes educativas
  0 - Sair

Escolha uma opcao: 5

--- RECOMENDACOES DE IRRIGACAO ---

Setor 1
  Risco de desperdicio: 30%
  Recomendacao:         MONITORAR
  Motivo:               Condicoes estaveis. Aguardar a proxima leitura.

Setor 2
  Risco de desperdicio: 60%
  Recomendacao:         NAO IRRIGAR
  Motivo:               Condicoes indicam alto risco de desperdicio.

Setor 3
  Risco de desperdicio: 0%
  Recomendacao:         IRRIGAR MODERADAMENTE
  Motivo:               Umidade abaixo do ideal. Aplicar irrigacao leve.
```

E ao calcular a economia:

```
--- ECONOMIA ESTIMADA ---
Consumo tradicional (referencia): 50,000 L
Consumo com AgroSmart:            8,333 L
Economia estimada:                41,667 L
Economia em reais:                R$ 500.00
```

## Regras de decisão (resumo)

- **Umidade**
  - `< 30%` → solo seco
  - `30% – 70%` → ideal
  - `> 70%` → solo encharcado
- **Temperatura**
  - `< 10 °C` → frio extremo
  - `10 – 32 °C` → ideal
  - `> 32 °C` → calor intenso
- **Risco de desperdício**: soma os pontos quando a umidade está alta,
  a temperatura muito baixa ou a luminosidade muito baixa (somando até 100%).
- **Recomendação final**: combina o risco com os limites de umidade e
  temperatura para definir a ação por setor.

Esses valores podem ser ajustados facilmente nas constantes do início do
arquivo `main.py`.

## Como a solução contribui

Ao tomar decisões baseadas em dados, em vez de irrigar a área inteira por
padrão, o AgroSmart pode reduzir significativamente o consumo de água e,
consequentemente, o custo de produção. Em uma propriedade de 10 hectares,
nos exemplos testados, a economia chegou a mais de **40.000 litros por
ciclo de irrigação**. Em larga escala, o impacto ambiental e financeiro é
ainda maior, contribuindo para uma agricultura mais sustentável.

## Integrantes do grupo

- Nome Completo 1 – RM XXXXXX
- Nome Completo 2 – RM XXXXXX
- Nome Completo 3 – RM XXXXXX
