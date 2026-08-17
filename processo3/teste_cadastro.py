from cadastro import executar_cadastro


cliente = {
    "nome": "Maria Santos",
    "email": "maria@email.com",
    "cpf": "98765432100",
    "simular_erro_api": False
}


resultado = executar_cadastro(cliente)


print("\nRESULTADO:")
print(resultado)