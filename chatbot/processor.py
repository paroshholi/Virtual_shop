import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
import os
from keras.models import load_model
from home.models import Product, Order, OrderItem
# Get the absolute path to the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the model file
model_path = os.path.join(current_dir, 'chatbot_model.h5')

# Load the model using the absolute path
model = load_model(model_path)
import json
import random
intents_file_path = os.path.join(current_dir, 'intents.json')
data_file = open(intents_file_path, encoding='utf-8').read()
intents = json.loads(data_file)
words_path = os.path.join(current_dir, 'words.pkl')
with open(words_path, 'rb') as f:
    words = pickle.load(f)
classes_path = os.path.join(current_dir, 'classes.pkl')
with open(classes_path, 'rb') as g:
    classes = pickle.load(g)



def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

  # Import the necessary models from your app's models.py

def getResponse(ints, intents_json, message, request):
    if request and request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = None
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for intent in list_of_intents:
        if intent['tag'] == tag:
            # Check if the intent is related to order
            if tag == 'order':
                # Fetch product keywords from the database
                product_keywords = Product.objects.values_list('name', flat=True)
                for keyword in product_keywords:
                    if keyword.lower() in message.lower():
                        # Add the product to the cart
                        product = Product.objects.get(name__iexact=keyword)
                        if current_user:
                            # Create or get the order for the current user with status 'ordered'
                            order, _ = Order.objects.get_or_create(customer=current_user, status='ordered')
                            # Create or get the order item for the product and order
                            order_item, _ = OrderItem.objects.get_or_create(order=order, product=product)
                            result = f"{keyword.capitalize()} has been added to your cart."
                        else:
                            result = "Please log in to add items to your cart."
                        break
                else:
                    result = "I'm sorry, I couldn't recognize the product."

            # Check if the intent is related to category
            elif tag == 'category':
                # Fetch category keywords from the database
                category_keywords = [choice[0] for choice in Product.CATEGORY_CHOICES]  # Assuming CATEGORY_CHOICES is defined in the Product model
                for keyword in category_keywords:
                    if keyword.lower() in message.lower():
                        # Fetch products belonging to this category from the database
                        products = Product.objects.filter(category=keyword)
                        product_names = ', '.join(product.name for product in products)
                        result = f"The products available in the {keyword} category are: {product_names}"
                        break
                else:
                    result = "I'm sorry, I couldn't recognize the category."
            elif tag == 'price':
                # Fetch product keywords from the database
                product_keywords = Product.objects.values_list('name', flat=True)
                for keyword in product_keywords:
                    if keyword.lower() in message.lower():
                        # Fetch the product and get its price
                        product = Product.objects.get(name__iexact=keyword)
                        result = f"The price of {product.name} is ₹{product.price}."
                        break
                else:
                    result = "I'm sorry, I couldn't recognize the product for which you asked the price."
            elif tag == 'remove_from_cart':
                # Fetch product keywords from the database
                product_keywords = Product.objects.values_list('name', flat=True)
                for keyword in product_keywords:
                    if keyword.lower() in message.lower():
                        # Remove the product from the cart
                        product = Product.objects.get(name__iexact=keyword)
                        if current_user:
                            # Get the order for the current user with status 'ordered'
                            order = Order.objects.get_or_create(customer=current_user, status='ordered')[0]
                            # Check if the product is in the user's cart
                            order_item = OrderItem.objects.filter(order=order, product=product).first()
                            if order_item:
                                order_item.delete()
                                result = f"{keyword.capitalize()} has been removed from your cart."
                            else:
                                result = f"{keyword.capitalize()} is not in your cart."
                        else:
                            result = "Please log in to remove items from your cart."
                        break
                else:
                    result = "I'm sorry, I couldn't recognize the product."
            else:
                responses = intent.get('responses', [])
                if responses:
                    result = random.choice(responses)
                else:
                    result = "I'm sorry, I couldn't understand."
            break
            
    else:
        result = "I'm sorry, I couldn't understand"
    return result


def chatbot_response(request,msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents, msg, request)
    return res