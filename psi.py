# PSI

# TO DO:
# Intersection should be computed on the clients end
# Split up parts by Client class and Server Class
# add benchmarking function regarding speed that creates tables
# function to take a hash and define it under a group G python
# start working on the readme project report

import random
from hashlib import blake2b


#### Preliminaries

# Simple paramaters used for demo purposes
P = 1019  # Large prime number for modulo operations
G = 2     # Primitive root modulo 

def hash_to_int(kwd):
    # Hash a keyword to an integer
    hash_value = blake2b(kwd.encode(), digest_size=16).digest()
    return int.from_bytes(hash_value, 'big')

def generate_secret():
    # Generate a random secret exponent
    return random.randint(1, P - 2)




def perform_psi(client_elements, server_elements_per_doc):
    # Perform PSI between the client and server

    # Client generates a secret and exponentiates their hashed elements
    client_secret = generate_secret()
    client_transformed_elements = [pow(G, elem * client_secret, P) for elem in client_elements]

    # Client sends the transformed elements to the server
    # Server generates a secret and exponentiates their hashed elements
    server_secret = generate_secret()
    counts = []
    for doc_id, server_elements in server_elements_per_doc.items():
        # Server exponentiates their elements and sends them to client
        server_transformed_elements = [pow(G, elem * server_secret, P) for elem in server_elements]

        # Server exponentiates client's elements with server's secret
        client_elements_server = [pow(elem, server_secret, P) for elem in client_transformed_elements]

        # Client exponentiates servers transformed elements with their secret and sends them back to server
        server_elements_client = [pow(elem, client_secret, P) for elem in server_transformed_elements]

        # Server finds the intersection
        set_client = set(client_elements_server)
        set_server = set(server_elements_client)
        intersection = set_client.intersection(set_server)
        count = len(intersection)
        counts.append((doc_id, count))

    # Server sends number of intersections back to the client
    return counts


# Server's keyword set
server_keywords = {'doc1': ['apple', 'banana', 'cherry', 'apple'],}

# Hash/encrypt server's keywords
server_elements_per_doc = {}
for doc_id, keywords in server_keywords.items():
    elements = []
    for kwd in keywords:
        elem = hash_to_int(kwd)
        elements.append(elem)
    server_elements_per_doc[doc_id] = elements

# Client inputs the keywords they wish to search for
user_input = input("Please enter keywords to search separated by spaces: ").strip()
client_keywords = [word for word in user_input.split() if word]

# Hash/encrypt client's keywords to integers
client_elements = [hash_to_int(kwd) for kwd in client_keywords]

# Perform PSI
counts = perform_psi(client_elements, server_elements_per_doc)

for doc_id, count in counts:
    print(f"Document '{doc_id}' has {count} matching keyword(s).")
