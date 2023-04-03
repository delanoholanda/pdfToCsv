docker rm -f pdfToCsv &&
docker build -t pdfToCsv:latest . &&
docker run -d -p 5000:5000 --name=pdfToCsv pdfToCsv  &&
docker logs --follow pdfToCsv
