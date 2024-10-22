from Business.settings import db
from bson import ObjectId
seller_collection = db['sellers']
product_collection = db['products']

class Seller:
    def __init__(self, dealer_name, company_name, address, phone_number, category, description,email_id, password, image, user_id):
        self.dealer_name = dealer_name
        self.company_name = company_name
        self.address = address
        self.phone_number = phone_number
        self.category = category
        self.description = description
        self.email_id = email_id
        self.password= password
        self.image = image
        self.user_id = user_id  # Link to the Django User ID


    def save(self):
        data = {
            "dealer_name": self.dealer_name,
            "company_name": self.company_name,
            "address": self.address,
            "phone_number": self.phone_number,
            "category": self.category,
            "description": self.description,
            "email_id": self.email_id,
            "password": self.password,
            "image": self.image,
            "user_id": self.user_id,  # Save the Django User ID in MongoDB
        }
        seller_collection.insert_one(data)

class Product:
    def __init__(self, category, storage_type, color, hdd_capacity, brand, product_model, price,
                 processor, battery_life, operating_system, ram, graphics_memory,product_description, image, seller_id):
        self.category = category
        self.storage_type = storage_type
        self.color = color
        self.hdd_capacity = hdd_capacity
        self.brand = brand
        self.product_model = product_model
        self.price = price
        self.processor = processor
        self.battery_life = battery_life
        self.operating_system = operating_system
        self.ram = ram
        self.graphics_memory = graphics_memory
        self.product_description = product_description
        self.image = image
        self.seller_id = seller_id  # Add seller's MongoDB ObjectId




    def save(self):
        data = {
            "category": self.category,
            "storage_type": self.storage_type,
            "color": self.color,
            "hdd_capacity": self.hdd_capacity,
            "brand": self.brand,
            "product_model": self.product_model,
            "price": self.price,
            "processor": self.processor,
            "battery_life": self.battery_life,
            "operating_system": self.operating_system,
            "ram": self.ram,
            "graphics_memory": self.graphics_memory,
            "product_description": self.product_description,
            "image": self.image, # Save the product image path in MongoDB
            "seller_id": ObjectId(self.seller_id),  # Store seller ObjectId in the product

        }
        product_collection.insert_one(data)
