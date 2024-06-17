from typing import List, Optional
from fastapi import FastAPI, HTTPException, Response,status
from fastapi.params import Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .routers import post,user,auth,vote

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Book(BaseModel):
    id:int
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

books : List[Book] = []

# while True:
#     try:
#         conn = psycopg2.connect(host='localhost',database='fastapi',
#                                 user='postgres',password='post123',cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("Database connect success")
#         break
#     except Exception as error:
#         print("DB Error:",error)
#         time.sleep(2)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/create")
def create(payload: dict = Body(...)):
    return {"message":f"title: {payload['title']} content:{payload['content']}"}

@app.post("/create2",status_code=status.HTTP_201_CREATED)
def create(payload: Book):
    return {"message":f"title: {payload.title} content:{payload.content}"}

@app.get("/book/{id}")
def root(id:int, respond: Response):
    print(type(id))

    if not isinstance(id,int):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="post no found")
        # respond.status_code = status.HTTP_400_BAD_REQUEST
        # return {'message':"post no found"}
    

    return {"message": f"book id is {id}"}

def find_index_book(id:int):
    for i, p in enumerate(books):
        if p['id'] == id:
            return i
        
def find_book(id:int):
    for p in enumerate(books):
        if p['id'] == id:
            return p

@app.delete("/book/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_book():
    index = find_index_book(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="no found")

    books.pop(index)

    # return {'message':"book delete successfully"}
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/book")
def update_book(book: Book):

    index = find_index_book(book.id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="no found")
    
    books[index] = book
    return {"data":book}