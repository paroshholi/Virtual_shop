from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from .models import Product,Order,Wishlist,OrderItem,OrderHistory,OrderedProduct
from django.db import transaction
from django.http import JsonResponse
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from chatbot import processor
from django.contrib.auth import authenticate

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        order, _ = Order.objects.get_or_create(customer=request.user, status='ordered')
        order_item, _ = OrderItem.objects.get_or_create(order=order, product=product)
        return JsonResponse({'message': 'Product added to cart successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def add_to_wishlist(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        wishlist, created = Wishlist.objects.get_or_create(customer=request.user)
        wishlist.products.add(product)
        return JsonResponse({'message': 'Product added to wishlist successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def wishlist_view(request):
    if request.user.is_authenticated:
        try:
            # Retrieve the wishlist for the current user
            wishlist = Wishlist.objects.get(customer=request.user)
            # Get all products in the wishlist
            wishlist_products = wishlist.products.all()
            return render(request, 'wishlist.html', {'wishlist_products': wishlist_products})
        except Wishlist.DoesNotExist:
            # If the wishlist doesn't exist, handle accordingly
            return render(request, 'wishlist.html', {'wishlist_products': None})
    else:
        # Handle the case where the user is not authenticated
        return render(request, 'wishlist.html', {'wishlist_products': None})



def cart_view(request):
    if request.user.is_authenticated:
        try:
            # Retrieve cart items for the current user
            cart_items = OrderItem.objects.filter(order__customer=request.user)
            
            # Calculate total price
            total_price = sum(item.total_price for item in cart_items)
            
            return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})
        except OrderItem.DoesNotExist:
            # Handle the case where there are no items in the cart
            cart_items = None
            total_price = 0
            prices = []
            return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price, 'prices': prices })
    else:
        # Redirect to the login page if the user is not authenticated
        return redirect('login')



def remove_from_cart(request, product_id):
    if request.user.is_authenticated:
        order = get_object_or_404(Order, customer=request.user, status='ordered')
        product = get_object_or_404(Product, pk=product_id)
        
        # Remove the order item associated with the product from the order
        order_item = get_object_or_404(OrderItem, order=order, product=product)
        order_item.delete()
        
        messages.success(request, 'Product removed from cart successfully')
        return redirect('cart')  # Redirect to the cart page after successful removal
    else:
        messages.error(request, 'User is not authenticated')
        return redirect('login')  # Redirect to the login page if the user is not authenticated


def remove_from_wishlist(request, product_id):
    if request.user.is_authenticated:
        wishlist = get_object_or_404(Wishlist, customer=request.user)
        product = get_object_or_404(Product, pk=product_id)
        wishlist.products.remove(product)
        messages.success(request, 'Product removed from wishlist successfully')
        return redirect('wishlist')  # Redirect to the wishlist page after successful removal
    else:
        messages.error(request, 'User is not authenticated')
        return redirect('login')  # Redirect to the login page if the user is not authenticated

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'product_detail.html', {'product': product})

def search_products(request):
    query = request.GET.get('q')
    if query:
        # Perform search query based on your logic
        results = Product.objects.filter(name__icontains=query)
        print(results)
    else:
        results = None
    return render(request, 'search.html', {'results': results, 'query': query})

def category_view(request, category):
    # Query products based on the category
    products = Product.objects.filter(category=category)
    return render(request, 'category.html', {'products': products, 'category': category})

def chatbot_response(request):
    if request.method == 'POST':
        the_question = request.POST.get('question')
        print(the_question)
        response = processor.chatbot_response(request, the_question)
        print(response)
        return JsonResponse({"response": response})
    else:
        return JsonResponse({"error": "Invalid request method"})



def update_quantity(request, product_id, new_quantity):
    # Retrieve the OrderItem based on the product ID
    order_item = get_object_or_404(OrderItem, product_id=product_id)

    # Update the quantity of the OrderItem
    order_item.quantity = new_quantity
    order_item.save()

    # You can return any data you need in the JSON response
    # For simplicity, you can just return a success message
    return JsonResponse({'message': 'Quantity updated successfully'})


@login_required
def confirm_purchase(request):
    if request.method == 'POST':
        # Retrieve the password from the request POST data
        password = request.POST.get('password')

        # Check if the provided password matches the user's password
        if request.user.check_password(password):
            # Use atomic transaction to ensure data integrity
            with transaction.atomic():
                cart_items = OrderItem.objects.filter(order__customer=request.user)
                total_price = sum(item.total_price for item in cart_items)
                order_history = OrderHistory.objects.create(customer=request.user, total_price=total_price)
                for cart_item in cart_items:
                    OrderedProduct.objects.create(order_history=order_history, product=cart_item.product, quantity=cart_item.quantity)
                
                # Clear the cart (delete all Order instances for the user)
                cart_items.delete()
            
            # Return a success response
            return JsonResponse({'success': True, 'message': 'Purchase successful'})
        else:
            # Return an error response if password does not match
            return JsonResponse({'success': False, 'message': 'Authentication failed. Incorrect password.'})
    else:
        # Handle other request methods if needed
        pass

def order_history(request):
    # Retrieve order history for the current user and prefetch related OrderedProduct instances
    order_history = OrderHistory.objects.filter(customer=request.user).prefetch_related('orderedproduct_set')
    return render(request, 'order_history.html', {'order_history': order_history})
