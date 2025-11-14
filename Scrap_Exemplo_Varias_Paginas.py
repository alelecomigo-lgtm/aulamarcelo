import requests
from bs4 import BeautifulSoup
import time
import csv
import psycopg2

DB_HOST = "dpg-d4b9ks75r7bs7391csug-a.oregon-postgres.render.com"
DB_NAME = "dbalexandre"
DB_USER = "admin"
DB_PASS = "N3ggq9r65Yx15dUZ4kC5m7lyNzoLJeHD"  
DB_PORT = "5432"

def inserir_livro(dados: dict):
    print('Inserindo dados no PostgreSQL...')
    conn = None
    try:
        # 1. Configuração de Conexão
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        cur = conn.cursor()

        # 2. Instrução SQL com PLACEHOLDERS (%s) - CORREÇÃO CRÍTICA
        # Não use f-string aqui!
        insert_query = """
            INSERT INTO livros (Titulo, Preco, Disponibilidade, Avaliacao, Pagina)
            VALUES (%s, %s, %s, %s, %s);
        """
        for dado in dados:
            values_tuple = (
                dado['Titulo'],
                dado['Preco'],
                dado['Disponibilidade'],
                dado['Avaliacao'],
                dado['Pagina']
             )
            # 4. Executando a instrução SQL com a TUPLA como segundo argumento - CORREÇÃO CRÍTICA
            cur.execute(insert_query, values_tuple)

            # Confirmando a transação
            conn.commit()
        print("Dados inseridos com sucesso no PostgreSQL")
        cur.close()

    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao conectar ou executar a query no PostgreSQL: {error}")
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()
            # print("Conexão com o PostgreSQL fechada.")

def converte_eur_real(valor):
    valor = valor.replace('£', '').strip()
    vlrConvertido = 0
    try:
        url = f"https://economia.awesomeapi.com.br/last/EUR-BRL"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            vlrConvertido = float(valor) * float(data["EURBRL"]["bid"])
    except Exception as e:
        print(f"Erro ao converter moeda: {e}")

    return round(vlrConvertido, 2)

def scrape_all_books():
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    all_books = []
    page = 1
    
    while True:
        url = base_url.format(page)
        print(f"Scraping pagina {page}: {url}")
        
        try:
            response = requests.get(url)
            if response.status_code == 404:
                print("Fim das paginas!")
                break
                
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            books = soup.find_all('article', class_='product_pod')
            
            if not books:
                break
                
            for book in books:
                title = book.h3.a['title']
                price = book.find('p', class_='price_color').text
                availability = book.find('p', class_='instock availability').text.strip()
                rating = book.p['class'][1] 
                if rating == 'One': 
                    rating = 1 
                elif rating == 'Two': 
                    rating = 2
                elif rating == 'Three': 
                    rating = 3
                elif rating == 'For': 
                    rating = 4
                else: rating = 5 
                all_books.append({
                    'Titulo': title,
                    'Preco': converte_eur_real(price),
                    'Disponibilidade': True if 'In stock' in availability else False,
                    'Avaliacao': rating,
                    'Pagina': int(page)
                })
            
            page += 1
            #if page == 3:
            #    break
            time.sleep(1)  # Respeitar o servidor
            
        except Exception as e:
            print(f"Erro na pagina {page}: {e}")
            break
    
    print(f"\nTotal de livros coletados: {len(all_books)}")
    return all_books

def save_to_csv(books_data):
    """Salva os dados em um arquivo CSV"""
    with open('livros.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=books_data[0].keys(),delimiter=';')
        writer.writeheader()
        writer.writerows(books_data)
    
    print("\nDados salvos em 'livros.csv'")

if __name__ == "__main__":
    livros = scrape_all_books()
    #save_to_csv(livros)
    inserir_livro(livros)
# Para usar:
# todos_livros = scrape_all_books()

