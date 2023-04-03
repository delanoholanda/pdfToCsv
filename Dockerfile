From python:3
COPY ./app /app
RUN pip install --upgrade pip
RUN pip install pandas
RUN pip install flask
RUN pip install waitress
RUN pip install tabula-py
WORKDIR /app
CMD python site_pdf_to_csv.py
