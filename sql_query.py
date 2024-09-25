import mysql.connector
import json
import os


connection = mysql.connector.connect(
    host="localhost", user="root", password="", database="cli_chatbot"
)
cursor = connection.cursor()


def load_product_data(cursor, json_path):
    print(f"Path: {json_path}")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as file:
            product_data = json.load(file)
    print(f"Total Products = {len(product_data)}")
    for product in product_data:
        product.update({"company_id": 4})
        title = product.get("Title")
        description = product.get("Description")
        discounted_price = product.get("Price", {}).get("Discounted Price")
        original_price = product.get("Price", {}).get("Original Price", None)
        pictures_list = product.get("Pictures", [])
        if pictures_list:
            pictures = ", ".join([pic for pic in pictures_list if pic])
        else:
            pictures = None
        company_id = product.get("company_id")
        insert_project_query = """
        INSERT INTO products (title, description, discounted_price, original_price, pictures, company_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            insert_project_query,
            (
                title,
                description,
                discounted_price,
                original_price,
                pictures,
                company_id,
            ),
        )
        cursor._connection.commit()
    print("Done")


def get_company_data():
    query = "SELECT * FROM companies"
    cursor.execute(query)
    companies = cursor.fetchall()
    return companies


if __name__ == "__main__":
    if connection.is_connected():
        print("Connected to MySQL database")
    product_json_path = "ref_data/random_product_data.json"
    load_product_data(cursor, product_json_path)
    # get_company_data()
