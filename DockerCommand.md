## To build the image
```docker build -t getting-started .```
## To run and build the container
```docker run -d --name musicapp -p 127.0.0.1:3000:3000 getting-started```
## To start an existing container
```docker start musicapp```