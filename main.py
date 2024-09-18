import os

import requests
from dotenv import load_dotenv

# Verifica se o token da Cloudflare está configurado
load_dotenv()

# # Verifica se existe o arquivo ip.txt
# try:
#     with open("database.txt", "r") as file:
#         saved_ip = file.read()
# except FileNotFoundError:
#     with open("database.txt", "w") as file:
#         file.write("")
#         saved_ip = ""
#         print("File created")

# Pega o IP atual
response = requests.get("https://api.ipify.org")
current_ip = "187.33.125.254"

# # Verifica se o IP atual é diferente do IP salvo
# if current_ip != saved_ip:
#     print("IP changed")
#     with open("database.txt", "w") as file:
#         file.write(current_ip)
# else:
#     print("IP not changed")
#     exit()


# Testa o token da Cloudflare
token = os.getenv("CLOUDFLARE_API_KEY")
if not token:
    print("Token not found")
    exit()

response = requests.get(
    "https://api.cloudflare.com/client/v4/user/tokens/verify",
    headers={"Authorization": "Bearer " + token},
    timeout=10,  # Timeout set to 10 seconds
)

if response.status_code != 200:
    print("Invalid token")
    exit()

# Lista as records da Cloudflare
response = requests.get(
    "https://api.cloudflare.com/client/v4/zones/"
    + os.getenv("CLOUDFLARE_ZONE_ID")
    + "/dns_records",
    headers={"Authorization": "Bearer " + token},
    timeout=10,  # Timeout set to 10 seconds
)

if response.status_code != 200:
    print("Error listing records")
    exit()

records = response.json()["result"]

for record in records:
    if record["type"] == "A":
        print("Updating record", record["name"])

        response = requests.put(
            "https://api.cloudflare.com/client/v4/zones/"
            + os.getenv("CLOUDFLARE_ZONE_ID")
            + "/dns_records/"
            + record["id"],
            headers={"Authorization": "Bearer " + token},
            json={
                "content": current_ip,
                "name": record["name"],
                "type": record["type"],
                "proxied": record["proxied"],
            },
            timeout=10,  # Timeout set to 10 seconds
        )

        if response.status_code != 200:
            print(
                "Error updating record "
                + record["name"]
                + " with content "
                + response.json()["errors"][0]["message"]
            )
            exit()
        else:
            print("Record " + record["name"] + " updated")
