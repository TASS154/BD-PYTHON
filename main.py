import json
import logging
import os
import random
import sys
from datetime import datetime


PASTA_LOGS = "logs"
PASTA_DADOS = "dados"
ARQUIVO_LOG = os.path.join(PASTA_LOGS, "agrosmart.log")
ARQUIVO_DADOS = os.path.join(PASTA_DADOS, "banco.json")

UMIDADE_SECO = 20
UMIDADE_IDEAL_MAX = 60
UMIDADE_UMIDO_MAX = 70

TEMP_BAIXA_MAX = 20
TEMP_IDEAL_MAX = 30

LUZ_BAIXA_MIN = 600
LUZ_IDEAL_MIN = 400

CUSTO_LITRO_AGUA = 0.012
CONSUMO_REFERENCIA_LHA = 5000

banco = {
    "agricultor": {},
    "propriedade": {},
    "setores": [],
    "leituras": []
}


def configurar_ambiente():
    os.makedirs(PASTA_LOGS, exist_ok=True)
    os.makedirs(PASTA_DADOS, exist_ok=True)
    logging.basicConfig(
        filename=ARQUIVO_LOG,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        encoding="utf-8",
    )
    logging.info("=== Sistema AgroSmart iniciado ===")


def salvar_dados():
    try:
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
            json.dump(banco, arquivo, indent=2, ensure_ascii=False)
        logging.info("Dados salvos em %s", ARQUIVO_DADOS)
    except OSError as erro:
        logging.error("Falha ao salvar dados: %s", erro)
        print(f"[ERRO] Nao foi possivel salvar os dados: {erro}")


def carregar_dados():
    global banco
    if not os.path.exists(ARQUIVO_DADOS):
        logging.info("Nenhum banco existente. Iniciando em branco.")
        return
    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
            banco = json.load(arquivo)
        logging.info("Dados carregados de %s", ARQUIVO_DADOS)
    except (OSError, json.JSONDecodeError) as erro:
        logging.warning("Falha ao carregar dados existentes: %s", erro)
        print(f"[AVISO] Banco anterior corrompido. Iniciando vazio. ({erro})")


def ler_texto(rotulo, obrigatorio=True):
    valor = input(rotulo).strip()
    if obrigatorio and not valor:
        raise ValueError("Este campo nao pode ficar em branco.")
    return valor


def ler_numero(rotulo, tipo=float, minimo=None, maximo=None):
    bruto = input(rotulo).strip().replace(",", ".")
    try:
        valor = tipo(bruto)
    except ValueError:
        raise ValueError(f"Valor invalido: '{bruto}'.")
    if minimo is not None and valor < minimo:
        raise ValueError(f"Valor deve ser maior ou igual a {minimo}.")
    if maximo is not None and valor > maximo:
        raise ValueError(f"Valor deve ser menor ou igual a {maximo}.")
    return valor


def cadastrar_agricultor():
    print("\n--- CADASTRO DO AGRICULTOR ---")
    try:
        nome = ler_texto("Nome completo: ")
        idade = ler_numero("Idade: ", tipo=int, minimo=1, maximo=120)
        cidade = ler_texto("Cidade/UF: ")
    except ValueError as erro:
        print(f"[ERRO] {erro}")
        logging.warning("Cadastro de agricultor invalido: %s", erro)
        return

    banco["agricultor"] = {
        "nome": nome,
        "idade": idade,
        "cidade": cidade,
        "cadastrado_em": datetime.now().isoformat(timespec="seconds"),
    }
    salvar_dados()
    logging.info("Agricultor cadastrado: %s", nome)
    print(f"\nAgricultor '{nome}' cadastrado com sucesso!")


def cadastrar_propriedade():
    print("\n--- CADASTRO DA PROPRIEDADE ---")
    if not banco["agricultor"]:
        print("[AVISO] Cadastre o agricultor primeiro.")
        return
    try:
        nome = ler_texto("Nome da propriedade: ")
        area = ler_numero("Area total (hectares): ", tipo=float, minimo=0.1)
        cultura = ler_texto("Cultura plantada (ex: soja, milho, cafe): ")
        qtd_setores = ler_numero(
            "Quantitade de setores monitorados (1-20): ",
            tipo=int, minimo=1, maximo=20,
        )
    except ValueError as erro:
        print(f"[ERRO] {erro}")
        logging.warning("Cadastro de propriedade invalido: %s", erro)
        return

    banco["propriedade"] = {
        "nome": nome,
        "area_hectares": area,
        "cultura": cultura,
    }
    banco["setores"] = [f"Setor {i + 1}" for i in range(qtd_setores)]
    salvar_dados()
    logging.info(
        "Propriedade cadastrada: %s (%s setores)", nome, qtd_setores
    )
    print(f"\nPropriedade '{nome}' cadastrada com {qtd_setores} setores!")


def ler_sensor_arduino(setor):
    return {
        "setor": setor,
        "umidade": round(random.uniform(0, 100), 1),
        "temperatura": round(random.uniform(8, 38), 1),
        "luminosidade": random.randint(0, 1023),
        "data_hora": datetime.now().isoformat(timespec="seconds"),
    }


def coletar_dados_ambientais():
    print("\n--- COLETA DE DADOS AMBIENTAIS ---")
    if not banco["setores"]:
        print("[AVISO] Cadastre a propriedade primeiro.")
        return

    print("Modos de coleta:")
    print("  1 - Automatica (simulacao Arduino)")
    print("  2 - Manual (digitar valores)")
    opcao = input("Opcao: ").strip()

    if opcao == "1":
        novas = []
        for setor in banco["setores"]:
            leitura = ler_sensor_arduino(setor)
            banco["leituras"].append(leitura)
            novas.append(leitura)
            print(
                f"  {setor}: umidade={leitura['umidade']}%  "
                f"temp={leitura['temperatura']}C  "
                f"luz(LDR)={leitura['luminosidade']}"
            )
        salvar_dados()
        logging.info("Coleta automatica registrada (%s setores).", len(novas))
        print(f"\n{len(novas)} leituras adicionadas ao historico.")

    elif opcao == "2":
        print("Setores disponiveis:", ", ".join(banco["setores"]))
        try:
            setor = ler_texto("Setor: ")
            if setor not in banco["setores"]:
                raise ValueError("Setor inexistente.")
            umidade = ler_numero(
                "Umidade do solo (%): ", tipo=float, minimo=0, maximo=100
            )
            temperatura = ler_numero(
                "Temperatura (C): ", tipo=float, minimo=-20, maximo=60
            )
            luminosidade = ler_numero(
                "Luz - valor do LDR (0-1023): ",
                tipo=int, minimo=0, maximo=1023,
            )
        except ValueError as erro:
            print(f"[ERRO] {erro}")
            logging.warning("Coleta manual invalida: %s", erro)
            return

        leitura = {
            "setor": setor,
            "umidade": umidade,
            "temperatura": temperatura,
            "luminosidade": luminosidade,
            "data_hora": datetime.now().isoformat(timespec="seconds"),
        }
        banco["leituras"].append(leitura)
        salvar_dados()
        logging.info("Coleta manual registrada para %s.", setor)
        print("Leitura registrada com sucesso!")

    else:
        print("[ERRO] Opcao invalida.")


def ultima_leitura_por_setor():
    ultimas = {}
    for leitura in banco["leituras"]:
        ultimas[leitura["setor"]] = leitura
    return ultimas


def classificar_umidade(umidade):
    if umidade < UMIDADE_SECO:
        return "SECO"
    if umidade <= UMIDADE_IDEAL_MAX:
        return "IDEAL"
    if umidade <= UMIDADE_UMIDO_MAX:
        return "UMIDO"
    return "EXCESSO"


def classificar_temperatura(temp):
    if temp < TEMP_BAIXA_MAX:
        return "BAIXA"
    if temp <= TEMP_IDEAL_MAX:
        return "IDEAL"
    return "ALTA"


def classificar_luz(ldr):
    if ldr > LUZ_BAIXA_MIN:
        return "BAIXA"
    if ldr > LUZ_IDEAL_MIN:
        return "IDEAL"
    return "ALTA"


def analisar_ambiente():
    print("\n--- ANALISE DE UMIDADE, TEMPERATURA E LUZ ---")
    ultimas = ultima_leitura_por_setor()
    if not ultimas:
        print("[AVISO] Nenhuma leitura registrada ainda.")
        return

    for setor, leitura in ultimas.items():
        print(f"\n{setor}  ({leitura['data_hora']})")
        print(
            f"  Umidade do solo: {leitura['umidade']}%  "
            f"-> {classificar_umidade(leitura['umidade'])}"
        )
        print(
            f"  Temperatura:     {leitura['temperatura']}C  "
            f"-> {classificar_temperatura(leitura['temperatura'])}"
        )
        print(
            f"  Luz (LDR):       {leitura['luminosidade']}  "
            f"-> {classificar_luz(leitura['luminosidade'])}"
        )


def calcular_risco_desperdicio(leitura):
    solo = classificar_umidade(leitura["umidade"])
    temp = classificar_temperatura(leitura["temperatura"])
    luz = classificar_luz(leitura["luminosidade"])

    risco = 0
    if solo == "EXCESSO":
        risco += 90
    elif solo == "UMIDO":
        risco += 60
    elif solo == "IDEAL":
        risco += 20

    if solo != "SECO":
        if temp == "BAIXA":
            risco += 10
        if luz == "BAIXA":
            risco += 10

    return min(risco, 100)


def gerar_recomendacao(leitura):
    solo = classificar_umidade(leitura["umidade"])
    temp = classificar_temperatura(leitura["temperatura"])
    luz = classificar_luz(leitura["luminosidade"])

    if solo == "EXCESSO":
        return ("NAO IRRIGAR",
                "Solo encharcado. Risco de doencas e perda de raiz.")
    if solo == "UMIDO":
        return ("NAO IRRIGAR",
                "Solo ja umido. Irrigar agora seria desperdicio.")
    if solo == "SECO" and temp == "ALTA" and luz == "ALTA":
        return ("IRRIGAR IMEDIATO",
                "Solo seco com calor e luz forte. Cultura em estresse idrico.")
    if solo == "SECO":
        return ("IRRIGAR URGENTE",
                "Solo seco. Cultura precisa de agua.")
    return ("MONITORAR",
            "Condicoes estaveis. Aguardar a proxima leitura.")


def exibir_recomendacoes():
    print("\n--- RECOMENDACOES DE IRRIGACAO ---")
    ultimas = ultima_leitura_por_setor()
    if not ultimas:
        print("[AVISO] Nenhuma leitura disponivel.")
        return

    for setor, leitura in ultimas.items():
        risco = calcular_risco_desperdicio(leitura)
        acao, motivo = gerar_recomendacao(leitura)
        print(f"\n{setor}")
        print(f"  Risco de desperdicio: {risco}%")
        print(f"  Recomendacao:         {acao}")
        print(f"  Motivo:               {motivo}")
        logging.info("%s: risco=%s%% acao=%s", setor, risco, acao)


def calcular_economia():
    print("\n--- ECONOMIA ESTIMADA ---")
    if not banco["propriedade"]:
        print("[AVISO] Cadastre a propriedade primeiro.")
        return
    ultimas = ultima_leitura_por_setor()
    if not ultimas:
        print("[AVISO] Nenhuma leitura registrada.")
        return

    area_total = banco["propriedade"]["area_hectares"]
    qtd_setores = len(banco["setores"]) or 1
    area_setor = area_total / qtd_setores

    consumo_padrao = CONSUMO_REFERENCIA_LHA * area_total

    consumo_inteligente = 0.0
    for _, leitura in ultimas.items():
        acao, _ = gerar_recomendacao(leitura)
        if acao in ("IRRIGAR IMEDIATO", "IRRIGAR URGENTE"):
            consumo_inteligente += CONSUMO_REFERENCIA_LHA * area_setor

    economia_litros = consumo_padrao - consumo_inteligente
    economia_reais = economia_litros * CUSTO_LITRO_AGUA

    print(f"Consumo tradicional (referencia): {consumo_padrao:,.0f} L")
    print(f"Consumo com AgroSmart:            {consumo_inteligente:,.0f} L")
    print(f"Economia estimada:                {economia_litros:,.0f} L")
    print(f"Economia em reais:                R$ {economia_reais:,.2f}")
    logging.info(
        "Economia: %.0f L (R$ %.2f)", economia_litros, economia_reais
    )


def mostrar_historico():
    print("\n--- HISTORICO DE LEITURAS ---")
    if not banco["leituras"]:
        print("Nenhuma leitura registrada.")
        return

    print(f"Total de registros: {len(banco['leituras'])}")
    print(
        f"{'Data/Hora':<22}{'Setor':<12}"
        f"{'Umid%':>8}{'Temp':>9}{'Luz':>8}"
    )
    print("-" * 60)
    for leitura in banco["leituras"][-15:]:
        print(
            f"{leitura['data_hora']:<22}"
            f"{leitura['setor']:<12}"
            f"{leitura['umidade']:>8}"
            f"{leitura['temperatura']:>9}"
            f"{leitura['luminosidade']:>8}"
        )


EXPLICACOES = {
    "1": (
        "Por que medir a umidade do solo?",
        "Irrigar com o solo ja umido desperdica agua, energia e nutrientes. "
        "Sensores de umidade permitem identificar o momento exato em que a "
        "planta realmente precisa de agua.",
    ),
    "2": (
        "Influencia da temperatura na irrigacao",
        "Em dias muito quentes, a evapotranspiracao aumenta e parte da agua "
        "se perde antes de chegar a raiz. Em dias frios, a planta consome "
        "muito menos agua. Considerar a temperatura evita perdas.",
    ),
    "3": (
        "O papel da luminosidade",
        "A luminosidade esta ligada a fotossintese e a evapotranspiracao. "
        "Em periodos de baixa luz (noite, dias nublados) a planta consome "
        "menos agua, e regar pode representar desperdicio.",
    ),
    "4": (
        "Como o AgroSmart contribui",
        "Integrando sensores Arduino a decisoes automatizadas, o sistema "
        "ajuda o agricultor a reduzir o consumo de agua, evitar perdas na "
        "lavoura e operar de forma mais sustentavel.",
    ),
}


def explicacoes_educativas():
    print("\n--- EXPLICACOES EDUCATIVAS ---")
    for chave, (titulo, _) in EXPLICACOES.items():
        print(f"  {chave} - {titulo}")
    print("  0 - Voltar")

    opcao = input("Escolha um topico: ").strip()
    if opcao == "0":
        return
    if opcao in EXPLICACOES:
        titulo, texto = EXPLICACOES[opcao]
        print(f"\n>> {titulo}\n{texto}")
        logging.info("Consulta de explicacao: %s", titulo)
    else:
        print("[ERRO] Topico invalido.")


def exibir_cabecalho():
    print("\n" + "=" * 60)
    print(" AGROSMART - Monitoramento Inteligente da Lavoura")
    print("=" * 60)
    if banco["agricultor"]:
        print(f" Agricultor:  {banco['agricultor']['nome']}")
    if banco["propriedade"]:
        prop = banco["propriedade"]
        print(
            f" Propriedade: {prop['nome']} | "
            f"{prop['area_hectares']} ha | {prop['cultura']}"
        )
    print("=" * 60)


def menu():
    opcoes = {
        "1": ("Cadastrar agricultor", cadastrar_agricultor),
        "2": ("Cadastrar propriedade", cadastrar_propriedade),
        "3": ("Coletar dados ambientais (Arduino)", coletar_dados_ambientais),
        "4": ("Analisar umidade e temperatura", analisar_ambiente),
        "5": ("Exibir recomendacoes de irrigacao", exibir_recomendacoes),
        "6": ("Calcular economia estimada", calcular_economia),
        "7": ("Mostrar historico de leituras", mostrar_historico),
        "8": ("Explicacoes educativas", explicacoes_educativas),
        "0": ("Sair", None),
    }

    while True:
        exibir_cabecalho()
        for chave, (descricao, _) in opcoes.items():
            print(f"  {chave} - {descricao}")

        try:
            escolha = input("\nEscolha uma opcao: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando...")
            break

        if escolha == "0":
            print("Encerrando AgroSmart. Ate logo!")
            logging.info("Sistema encerrado pelo usuario.")
            break

        item = opcoes.get(escolha)
        if not item:
            print("[ERRO] Opcao invalida.")
            continue

        _, funcao = item
        try:
            funcao()
        except Exception as erro:
            logging.exception("Erro inesperado na opcao %s: %s", escolha, erro)
            print(f"[ERRO] Algo deu errado: {erro}")


if __name__ == "__main__":
    configurar_ambiente()
    carregar_dados()
    try:
        menu()
    except Exception as erro:
        logging.exception("Erro fatal: %s", erro)
        print(f"[ERRO FATAL] {erro}")
        sys.exit(1)
