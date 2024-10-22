from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from bson import ObjectId
import os

from .models import Seller, Product, seller_collection, product_collection


# Function to create a JWT for a user
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# Home View
@api_view(['GET'])
def home(request):
    return Response({"message": "Welcome to Seller API"})


# Register Seller View
@api_view(['POST'])
def add_seller(request):
    data = request.data
    dealer_name = data.get('dealer_name')
    company_name = data.get('company_name')
    address = data.get('address')
    phone_number = data.get('phone_number')
    category = data.get('category')
    description = data.get('description')
    email_id = data.get('email_id')
    password = data.get('password')
    image = data.get('image')

    if not all([dealer_name, company_name, address, phone_number, category, description, email_id, password, image]):
        return Response({"error": "Not all required data is provided."}, status=400)

    # Create Django User for the seller
    user = User.objects.create(
        username=dealer_name,
        password=make_password(password),
        email=email_id
    )

    # Save the image
    # image_path = None
    # if image and isinstance(image, InMemoryUploadedFile):
    #     image_path = default_storage.save(os.path.join('sellers', image.name), image)

    # Store seller data in MongoDB
    seller = Seller(dealer_name, company_name, address, phone_number, category, description,email_id, password, image, user.id)
    seller.save()

    return Response({"message": "Seller added successfully"}, status=201)


# Seller Login View
@api_view(['POST'])
def seller_login(request):
    data = request.data
    email = data.get('email_id')
    password = data.get('password')

    try:
        user = User.objects.get(email=email)

        if not user.check_password(password):
            return Response({"error": "Invalid credentials"}, status=400)

        # Generate JWT token
        tokens = get_tokens_for_user(user)
        return Response(tokens, status=200)

    except User.DoesNotExist:
        return Response({"error": "Invalid username or password"}, status=400)


# Add Product View (with seller association)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product(request):
    user = request.user
    data = request.data

    category = data.get('category')
    storage_type = data.get('storage_type')
    color = data.get('color')
    hdd_capacity = data.get('hdd_capacity')
    brand = data.get('brand')
    product_model = data.get('product_model')
    price = data.get('price')
    processor = data.get('processor')
    battery_life = data.get('battery_life')
    operating_system = data.get('operating_system')
    ram = data.get('ram')
    graphics_memory = data.get('graphics_memory')
    product_description = data.get('product_description')
    image = data.get('image')

    if not all(
            [category, storage_type, color, hdd_capacity, brand, product_model, price, processor,
             battery_life, operating_system, ram, graphics_memory, product_description, image]):
        return Response({"error": "Not all required data is provided."}, status=400)

    # Get seller by user_id (from Django user model)
    seller = seller_collection.find_one({"user_id": user.id})

    if not seller:
        return Response({"error": "Seller not found."}, status=400)

    seller_id = seller['_id']

    # Save the image
    # image_path = None
    # if image and isinstance(image, InMemoryUploadedFile):
    #     image_path = default_storage.save(os.path.join('products', image.name), image)

    # Add seller_id to the product
    product = Product(category, storage_type, color, hdd_capacity, brand, product_model, price, processor, battery_life, operating_system, ram, graphics_memory, product_description,image, seller_id)
    product.save()
    return Response({"message": "Product added successfully"}, status=201)


# Search View
@api_view(['GET'])
def search_items(request):
    query = request.query_params.get('query', '').strip()

    if not query:
        return JsonResponse({"error": "Query parameter is required."}, status=400)

    # Search sellers by company name, address, phone number, or email_id
    seller_search = seller_collection.find({
        "$or": [
            {"dealer_name": {"$regex": query, "$options": "i"}},
            {"company_name": {"$regex": query, "$options": "i"}},
            {"address": {"$regex": query, "$options": "i"}},
            {"phone_number": {"$regex": query, "$options": "i"}},
            {"email_id": {"$regex": query, "$options": "i"}},
            {"category": {"$regex": query, "$options": "i"}},
        ]
    })

    # If sellers are found based on seller info
    sellers = list(seller_search)
    if sellers:
        # Return all matching sellers
        result = []
        for seller in sellers:
            seller_info = {
                "dealer_name": seller["dealer_name"],
                "company_name": seller["company_name"],
                "address": seller["address"],
                "phone_number": seller["phone_number"],
                "email_id": seller["email_id"],
                "category": seller["category"],
                "description": seller["description"],
            }
            result.append(seller_info)
        return JsonResponse({"sellers": result}, status=200)

    # If no sellers are found based on seller info, search products
    product_search = product_collection.find({
        "$or": [
            {"category": {"$regex": query, "$options": "i"}},
            {"product_description": {"$regex": query, "$options": "i"}},
            {"storage_type": {"$regex": query, "$options": "i"}},
            {"color": {"$regex": query, "$options": "i"}},
            {"hdd_capacity": {"$regex": query, "$options": "i"}},
            {"brand": {"$regex": query, "$options": "i"}},
            {"product_model": {"$regex": query, "$options": "i"}},
            {"price": {"$regex": query, "$options": "i"}},
            {"processor": {"$regex": query, "$options": "i"}},
            {"battery_life": {"$regex": query, "$options": "i"}},
            {"operating_system": {"$regex": query, "$options": "i"}},
            {"ram": {"$regex": query, "$options": "i"}},
            {"graphics_memory": {"$regex": query, "$options": "i"}},
        ]
    })

    # If products are found based on product info
    products = list(product_search)
    if products:
        seller_ids = {str(product["seller_id"]) for product in products}
        # Find sellers who own these products
        sellers_related = seller_collection.find({"_id": {"$in": [ObjectId(sid) for sid in seller_ids]}})

        result = []
        for seller in sellers_related:
            seller_info = {
                "dealer_name": seller["dealer_name"],
                "company_name": seller["company_name"],
                "address": seller["address"],
                "phone_number": seller["phone_number"],
                "email_id": seller["email_id"],
                "category": seller["category"],
                "description": seller["description"],
            }
            result.append(seller_info)
        return JsonResponse({"sellers": result}, status=200)

    # If no results found
    return JsonResponse({"message": "No matching sellers or products found."}, status=404)
