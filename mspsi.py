# MS-PSI

import random
from hashlib import blake2b
from collections import Counter

# Simple parameters used for demo purposes
P = 1019  # Large prime number for modulo operations
G = 2     # Primitive root modulo

def hash_to_int(kwd):
    # Hash a keyword to an integer
    hash_value = blake2b(kwd.encode(), digest_size=16).digest()
    return int.from_bytes(hash_value, 'big')

def generate_secret():
    # Generate a random secret exponent
    return random.randint(1, P - 2)

def perform_ms_psi(client_elements, server_elements_per_doc):
    # Perform MS-PSI between the client and server

    # Client generates a secret and exponentiates their hashed elements
    client_secret = generate_secret()
    client_element_counts = Counter(client_elements) # Client initiates counter to ensure that duplicates can be accounted for 
    client_transformed_counts = {}
    for elem, count in client_element_counts.items():
        transformed_elem = pow(G, elem * client_secret, P)
        client_transformed_counts[transformed_elem] = count

    # Client sends the transformed elements to the server
    # Server generates a secret and exponentiates their hashed elements per document
    server_secret = generate_secret()
    counts_per_doc = []
    for doc_id, server_elements in server_elements_per_doc.items():
        # Server exponentiates their elements and sends them to client
        server_element_counts = Counter(server_elements)
        server_transformed_counts = {}
        for elem, count in server_element_counts.items():
            transformed_elem = pow(G, elem * server_secret, P)
            server_transformed_counts[transformed_elem] = count

        # Server exponentiates client's elements with server's secret
        client_elements_server = {}
        for elem, count in client_transformed_counts.items():
            transformed_elem = pow(elem, server_secret, P)
            client_elements_server[transformed_elem] = count

        # Client exponentiates servers transformed elements with their secret and sends them back to server
        server_elements_client = {}
        for elem, count in server_transformed_counts.items():
            transformed_elem = pow(elem, client_secret, P)
            server_elements_client[transformed_elem] = count

        # Server finds multiset intersection (considering multiplicities)
        intersection_counts = {}
        for elem in client_elements_server:
            if elem in server_elements_client:
                min_count = min(client_elements_server[elem], server_elements_client[elem])
                intersection_counts[elem] = min_count

        # Sum the counts of the intersected elements
        total_count = sum(intersection_counts.values())
        counts_per_doc.append((doc_id, total_count))

    # Server sends number of intersections back to client
    return counts_per_doc

# Server's keyword sets
server_documents = {
    'doc1': ['apple', 'banana', 'cherry', 'apple'],
    'doc2': ['banana', 'date', 'fig', 'banana'],
    'doc3': ['cherry', 'date', 'grape', 'date'],
    'doc4': ['apple', 'date', 'kiwi', 'date'],
    'doc5': ['banana', 'cherry', 'lemon', 'banana', 'cherry']
}

# Hash/encrypt server's keywords per document
server_elements_per_doc = {}
for doc_id, keywords in server_documents.items():
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

# Perform MS-PSI
counts_per_doc = perform_ms_psi(client_elements, server_elements_per_doc)

for doc_id, count in counts_per_doc:
    print(f"Document '{doc_id}' has {count} matching keyword(s).")
