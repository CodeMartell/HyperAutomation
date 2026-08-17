import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ))


from processo3.cadastro import executar_cadastro
from processo4.sac import executar_sac
from processo5.relatorios import executar_relatorios


def testar_processo5():

    cliente = {
        "nome": "Maria Santos",
        "email": "maria@email.com",
        "cpf": "98765432100",
        "simular_erro_api": False
    }

    print("\n===== PROCESSO 3 =====")

    resultado_p3 = executar_cadastro(cliente)

    print(resultado_p3)


    print("\n===== PROCESSO 4 =====")

    resultado_p4 = executar_sac(resultado_p3)

    print(resultado_p4)


    print("\n===== PROCESSO 5 =====")

    resultado_p5 = executar_relatorios(resultado_p4)

    print("\nRESULTADO FINAL:")

    print(resultado_p5)

    assert resultado_p5["sucesso"] is True
    assert resultado_p5["status"] == "PROCESSO_CONCLUIDO"

    print("\n✅ PROCESSO 5 EXECUTADO COM SUCESSO")


if __name__ == "__main__":
    testar_processo5()