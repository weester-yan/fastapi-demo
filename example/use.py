from fastapi import FastAPI, Query, Path
from pydantic import BaseModel, Field
from typing import Annotated


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
