from pathlib import Path

from boto3 import resource as aws  # type: ignore
from fastapi import Cookie, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

DATABASE: str = "Test"
PASSHASH: str = "Test"


app = FastAPI(default_response_class=HTMLResponse)
database = aws("dynamodb").Table(DATABASE)

jinja = Jinja2Templates(Path(__file__).parent / "template").TemplateResponse


@app.get("/")
def home(request: Request, passhash: str = Cookie("")) -> HTMLResponse:
	if not isinstance(
		sections := (
			database.get_item(Key={"title": "All"})
			.get("Item", {})
			.get("section")
		),
		list,
	):
		raise HTTPException(
			status.HTTP_500_INTERNAL_SERVER_ERROR,
			"Internal Error Occurred",
		)

	return jinja(
		request,
		"home.html",
		context={
			"sections": sections,
			"admin": passhash == PASSHASH,
		},
	)
