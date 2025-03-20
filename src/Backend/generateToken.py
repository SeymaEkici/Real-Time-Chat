from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/token", response_model=Token)
async def login_for_access_token(username: str, password: str):
    # Burada kullanıcı adı ve şifreyi doğrulamalısın
    # Örneğin, bir veritabanı sorgusu yapabilirsin.
    # Eğer doğrulama başarılıysa, token oluşturulacak.
    
    # Token oluşturma
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {"sub": username, "exp": datetime.utcnow() + access_token_expires},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {"access_token": access_token, "token_type": "bearer"}
