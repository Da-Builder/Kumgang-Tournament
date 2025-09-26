# Import Dependencies
from boto3 import resource as aws  # type: ignore
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Application Enviroments
DATABASE: str = "Test"
PASSHASH: str = "Test"


# Application Setups
app = FastAPI(default_response_class=HTMLResponse)
database = aws("dynamodb").Table(DATABASE)
jinja = Jinja2Templates("template").TemplateResponse


# Application Endpoints
@app.get("/")
def home(request: Request) -> HTMLResponse:
	if not isinstance(
		sections := database.get_item(Key={"name": "All"})
		.get("Item", {})
		.get("sections"),
		list,
	):
		raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

	return jinja(
		request,
		"home.html",
		context={
			"sections": sections,
			"admin": verify_passhash(request.cookies.get("passhash")),
		},
	)


@app.get("/login")
def login(request: Request) -> HTMLResponse:
	return jinja(request, "login.html")


@app.get("/section/{name}")
def section(request: Request, name: str) -> HTMLResponse:
	if (section := database.get_item(Key={"name": name}).get("Item")) is None:
		raise HTTPException(status.HTTP_404_NOT_FOUND)

	if not isinstance(people := section.get("people"), list):
		raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

	return jinja(
		request,
		"section.html",
		context={
			"podium": (
				section.get("gold"),
				section.get("silver"),
				section.get("bronze"),
			)[: min(3, len(people))],
			"people": {idx: person for idx, person in enumerate(people)},
			"admin": verify_passhash(request.cookies.get("passhash")),
		},
	)


# Utility Functions
def verify_passhash(passhash: str | None) -> bool:
	return passhash == PASSHASH
