"""
Before running this script, you should run an nginx docker container
to serve static files. Using the default image, run the following.

```
$ docker run \
        --name NAME \
        -v /path/to/asyncloop/examples/nginx-staticfiles:/usr/share/nginx/html:ro \
        -d \
        -p 8080:80 \
        nginx
```

Or check the Dockerhub repository (https://hub.docker.com/_/nginx).
"""
import aiohttp

from asyncloop import AsyncLoop


URLS = [
    'http://localhost:8080',
    'http://localhost:8080/first.html',
    'http://localhost:8080/second.html',
    'http://localhost:8080/third.html',
    'http://localhost:8080/fourth.html',
    'http://localhost:8080/fifth.html',
]

aloop = AsyncLoop(maxsize=30)


async def get(url):
    """A simplest GET using aiohttp."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await (response.text())


def main():
    for _ in range(1000):
        for url in URLS:
            aloop.submit(get(url))

    aloop.start()
    aloop.monitor()


if __name__ == '__main__':
    main()
