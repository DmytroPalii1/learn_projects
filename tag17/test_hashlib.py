import hashlib
passwort="mein_passwort123"
passwort_hash=hashlib.sha256(passwort.encode()).hexdigest()
print("Original:",passwort)
print("Hash:",passwort_hash)