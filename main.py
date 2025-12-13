import click
import uvicorn
from app.config import settings

@click.group()
def cli():
    """Analytics"""
    pass

@cli.command()
def server():
    uvicorn.run(
            "app.server:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug
        )

if __name__ == "__main__":
      cli()
