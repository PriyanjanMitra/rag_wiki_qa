from config import config


def main():
    import uvicorn
    uvicorn.run("route.api:app", host=config.host, port=config.port, reload=True)


if __name__ == "__main__":
    main()
