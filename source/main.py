# Import Dependencies
from os import environ

from boto3 import resource as aws  # type: ignore
from fastapi import Body, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as BaseHTTPException

# Application Enviroments
DATABASE: str = environ["DATABASE"]
PASSHASH: str = environ["PASSHASH"]


# Application Setups
app = FastAPI(default_response_class=HTMLResponse, openapi_url=None)
database = aws("dynamodb").Table(DATABASE)
jinja = Jinja2Templates("template").TemplateResponse


# Application Endpoints
@app.get("/")
def home(request: Request) -> HTMLResponse:
	return jinja(
		request,
		"home.html",
		context={
			"sections": database.get_item(Key={"name": "All"})
			.get("Item", {})
			.get("sections"),
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
			"podium": tuple(
				people[int(rank)]
				if (rank := str(section.get(medal))).isdecimal()
				else None
				for medal in ("gold", "silver", "bronze")
			)[: min(3, len(people))],
			"people": {idx: person for idx, person in enumerate(people)},
			"admin": verify_passhash(request.cookies.get("passhash")),
		},
	)


@app.put("/section")
def section_update(
	request: Request,
	section: str = Body(),
	rank: str = Body(),
	person: str = Body(),
	person_id: int = Body(),
) -> None:
	if not verify_passhash(request.cookies.get("passhash")):
		raise HTTPException(status.HTTP_401_UNAUTHORIZED)

	if not person:
		raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE)

	if person_id < 0:
		database.update_item(
			Key={"name": section},
			UpdateExpression="SET people = list_append(people, :person)",
			ExpressionAttributeValues={":person": [person]},
		)
		return

	expression: str = f"SET people[{person_id}] = :person"
	attributes: dict[str, int | str] = {":person": person}

	if rank in {"gold", "silver", "bronze"}:
		expression += f", {rank} = :rank"
		attributes.update({":rank": person_id})

	database.update_item(
		Key={"name": section},
		UpdateExpression=expression,
		ExpressionAttributeValues=attributes,
	)


@app.exception_handler(BaseHTTPException)
def http_handler(
	request: Request, exception: BaseHTTPException
) -> HTMLResponse:
	return render_error(request, exception.status_code, exception.detail)


@app.exception_handler(Exception)
def database_handler(request: Request, exception: Exception) -> HTMLResponse:
	return render_error(request)


# Utility Functions
def verify_passhash(passhash: str | None) -> bool:
	return passhash == PASSHASH


def render_error(
	request: Request,
	code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
	message: str = "Internal Server Error",
) -> HTMLResponse:
	return jinja(
		request,
		"error.html",
		status_code=code,
		context={"code": code, "message": message},
	)
