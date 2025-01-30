from typing import Annotated, Iterator

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse

from helpers.image import extract_board_from_image_bytes
from solvers.simple import solve_color_fill_simple

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("index.html", "r") as f:
        return HTMLResponse(f.read())


@app.post("/solve")
async def solve(
    depth: Annotated[int, Form()] = 4,
    file: UploadFile = File(...),
) -> StreamingResponse:
    board = extract_board_from_image_bytes(await file.read())

    def solution_generator() -> Iterator[str]:
        yield from solve_color_fill_simple(board, max_depth=depth)

    return StreamingResponse(
        solution_generator(),
        media_type="application/json",
    )
