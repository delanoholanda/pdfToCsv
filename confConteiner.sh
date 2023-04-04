docker rm -f pdftocsv &&
docker build -t pdftocsv:latest . &&
docker run -d -p 8091:5000 --name=pdftocsv pdftocsv  &&
docker logs --follow pdftocsv
