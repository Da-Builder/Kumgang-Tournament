# Import Dependencies
from json import load
from pathlib import Path
from sys import argv

from boto3 import resource as aws  # type: ignore


# Main Function
def main() -> None:
	if len(argv) != 2:
		return print(f"Usage: python {argv[0]} [DATABASE]")

	database = aws("dynamodb").Table(argv[1])
	with open(Path(__file__).parent / "data.json") as file:
		data: dict[str, list[str]] = load(file)

	database.put_item(
		Item={
			"name": "All",
			"sections": [(section, None) for section in data],
		}
	)

	for section, people in data.items():
		database.put_item(Item={"name": section, "people": people})


# Script Entrypoint
if __name__ == "__main__":
	main()
