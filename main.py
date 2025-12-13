import click
import uvicorn
from app.config import settings
from app.handlers.files_processor import Processor

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

@cli.command()
def processor():
    proc = Processor()
    try:
        proc.run()
    except KeyboardInterrupt:
        print("\nShutting down processor...")
        proc.subscriber.close()
        print("Processor stopped.")

if __name__ == "__main__":
      cli()
