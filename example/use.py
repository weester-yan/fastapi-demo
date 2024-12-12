from fastapi import FastAPI, Query, Path, Form, File, UploadFile, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Annotated
from enum import Enum
from datetime import datetime



app = FastAPI()


# 基础路由
@app.get("/")
async def root():
    return "Test"


# 路径参数
@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}


# 路径参数，声明类型
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


# 路径参数，预设枚举值
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}


# 路径参数，校验
# 使用Path声明
@app.get("/items/{item_id}")
async def read_items(
    *,
    item_id: int = Path(title="The ID of the item to get", ge=0, le=1000),
    q: str,
    size: float = Query(gt=0, lt=10.5),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if size:
        results.update({"size": size})
    return results


# 查询参数
# 本例中有 3 个查询参数：
#   needy，必选的 str 类型参数
#   skip，默认值为 0 的 int 类型参数
#   limit，可选的 int 类型参数
@app.get("/items/{item_id}")
async def read_user_item(
    item_id: str, needy: str, skip: int = 0, limit: int | None = None
):
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item


# 查询参数校验
# 使用Query
@app.get("/items/")
async def read_items(
    q: Union[str, None] = Query(
        default=None,		# 默认值，同时表示参数可选
        alias="item-query",	# 参数别名，http://localhost:8000/items/?item-query=test
        title="Query string",	# 参数信息，API文档使用
        description="Query string for the items to search in the database that have a good match",
        min_length=3,		# 参数最短长度校验
        max_length=50,		# 参数最长长度校验
        pattern="^fixedquery$",	# 参数正则校验
        deprecated=True,	# 参数保留使用，在文档中表示为已弃用
    ),
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# 请求体
# 一般使用Pydantic声明请求体
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.post("/create"):
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


# 请求体，多参数
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

class User(BaseModel):
    username: str
    full_name: str | None = None

@app.put("/items/{item_id}")
async def update_item(
    item_id: int, item: Item, user: User, importance: Annotated[int, Body()]
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results
# 期望传入请求体
#{
#    "item": {
#        "name": "Foo",
#        "description": "The pretender",
#        "price": 42.0,
#        "tax": 3.2
#    },
#    "user": {
#        "username": "dave",
#        "full_name": "Dave Grohl"
#    },
#    "importance": 5
#}


# 使用Pydantic Field声明参数
class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
    results = {"item_id": item_id, "item": item}
    return results


# 表单
class FormData(BaseModel):
    username: str
    password: str

@app.post("/login/")
async def login(data: Annotated[FormData, Form()]):
    return data


# 文件上传
@app.post("/files/")
async def create_file(file: bytes | None = File(default=None)):
    if not file:
        return {"message": "No file sent"}
    else:
        return {"file_size": len(file)}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile | None = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        return {"filename": file.filename}
# 文件作为「表单数据」上传。
# 如果把路径操作函数参数的类型声明为 bytes，FastAPI 将以 bytes 形式读取和接收文件内容。
# 这种方式把文件的所有内容都存储在内存里，适用于小型文件。
# 不过，很多情况下，UploadFile 更好用。
# UploadFile 与 bytes 相比有更多优势：
#   - 使用 spooled 文件：
#     - 存储在内存的文件超出最大上限时，FastAPI 会把文件存入磁盘；
#   - 这种方式更适于处理图像、视频、二进制文件等大型文件，好处是不会占用所有内存；
#   - 可获取上传文件的元数据；
# UploadFile 的属性如下：
#   - filename：上传文件名字符串（str），例如， myimage.jpg；
#   - content_type：内容类型（MIME 类型 / 媒体类型）字符串（str），例如，image/jpeg；
#   - file： SpooledTemporaryFile（ file-like 对象）。其实就是 Python文件，可直接传递给其他预期 file-like 对象的函数或支持库。
# UploadFile 支持以下 async 方法，（使用内部 SpooledTemporaryFile）可调用相应的文件方法。
#   - write(data)：把 data （str 或 bytes）写入文件；
#   - read(size)：按指定数量的字节或字符（size (int)）读取文件内容；
#   - seek(offset)：移动至文件 offset （int）字节处的位置；
#     - 例如，await myfile.seek(0) 移动到文件开头；
#     - 执行 await myfile.read() 后，需再次读取已读取内容时，这种方法特别好用；
#   - close()：关闭文件


## 多文件上传
@app.post("/files/")
async def create_files(files: list[bytes] = File()):
    return {"file_sizes": [len(file) for file in files]}

@app.post("/uploadfiles/")
async def create_upload_files(files: list[UploadFile]):
    return {"filenames": [file.filename for file in files]}


## 错误处理
@app.get("/items-header/{item_id}")
async def read_item_header(item_id: str):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"},		# 支持自定义header
        )
    return {"item": items[item_id]}


## JSON格式处理
fake_db = {}
class Item(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None

@app.put("/items/{id}")
def update_item(id: str, item: Item):
    json_compatible_item_data = jsonable_encoder(item)
    fake_db[id] = json_compatible_item_data
# 在这个例子中，它将Pydantic模型转换为dict，并将datetime转换为str。
# 调用它的结果后就可以使用Python标准编码中的json.dumps()


## CORS跨域
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




### Start this server
#
# uvicorn main:app --reload --host 127.0.0.1 --port 8000
#
# uvicorn main:app 命令含义如下:
#   main：main.py 文件（一个 Python「模块」）。
#   app：在 main.py 文件中通过 app = FastAPI() 创建的对象。
#   --reload：让服务器在更新代码后重新启动。仅在开发时使用该选项。
#   --host：指定host，默认为localhost
#   --port：指定port，默认为8000
#
