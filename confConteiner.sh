docker rm -f csv &&
docker build -t csv:latest . &&
docker run -d -p 5000:5000 --name=csv csv  &&
docker logs --follow csv
