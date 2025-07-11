# import requests
# from bs4 import BeautifulSoup
# from rich import print


# def main():
#     url = "https://seia.sea.gob.cl/expediente/ficha/fichaPrincipal.php?modo=normal&id_expediente=2159071750"
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Check if the request was successful

#         soup = BeautifulSoup(response.content, 'html.parser')

#         # Extract the project name
#         project_name = soup.find('td', text='Proyecto').find_next_sibling('td').text.strip()

#         # Extract the project type
#         project_type = soup.find('td', text='Tipo de Proyecto').find_next_sibling('td').text.strip()

#         # Extract the investment amount
#         investment_amount = soup.find('td', text='Monto de Inversión').find_next_sibling('td').text.strip()

#         # Extract the current status
#         current_status = soup.find('td', text='Estado Actual').find_next_sibling('td').text.strip()

#         # Extract the project description
#         description = soup.find('td', text='Descripción del Proyecto').find_next_sibling('td').text.strip()

#         # Print the extracted information
#         print(f"Project Name: {project_name}")
#         print(f"Project Type: {project_type}")
#         print(f"Investment Amount: {investment_amount}")
#         print(f"Current Status: {current_status}")
#         print(f"Description: {description}")

#     except requests.exceptions.RequestException as e:
#         print(f"An error occurred: {e}")

# if __name__ == "__main__":
#     main()
