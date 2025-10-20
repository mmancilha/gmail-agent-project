import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# O SCOPE AQUI DEVE SER IGUAL AO DO NOSSO app/gmail_service.py
# Isto garante que o token terá as permissões corretas.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def main():
    """
    Executa o fluxo de autenticação para obter e imprimir um refresh token.
    """
    creds = None
    
    # O ficheiro token.json armazena os tokens de acesso e de atualização do utilizador.
    # Ele é criado automaticamente quando o fluxo de autorização é concluído pela primeira vez.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
    # Se não houver credenciais (válidas), permite que o utilizador faça login.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Carrega o ficheiro secrets do cliente a partir de credentials.json
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            
        # Guarda as credenciais para a próxima execução
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # Imprime o refresh token para que o possamos usar na nossa API
    if creds.refresh_token:
        print("\n--- O SEU NOVO REFRESH TOKEN ---")
        print(creds.refresh_token)
        print("--- Copie e use este token para registar um novo agente na sua API ---\n")
    else:
        print("\nNão foi possível obter um novo refresh token.")
        print("Pode ser necessário revogar o acesso da aplicação na sua conta Google e tentar novamente.")
        print("Aceda a: https://myaccount.google.com/permissions")


if __name__ == "__main__":
    main()