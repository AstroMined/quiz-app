import secrets

def generate_secure_token(nbytes=8):
    # Generate a secure random base64-encoded string.
    # The number of bytes specified will determine the randomness.
    # We adjust nbytes to get closer to a 64-character output, 
    # but due to base64 encoding, exact length can't be guaranteed.
    token = secrets.token_urlsafe(nbytes)
    return token

# Generate a random 64-bit ASCII string
random_string = generate_secure_token(48)  # Adjusted nbytes for a longer output
print(random_string)
