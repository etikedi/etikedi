FROM python:3.8.2-buster

WORKDIR /app
RUN pip install pipenv

# Install runtime and development dependencies
COPY Pipfile* ./
RUN pipenv install --dev --system

# Install packages for the NLTK (Natural Language Toolkit)
RUN (echo "import nltk"; echo "nltk.download('averaged_perceptron_tagger')") | python

# Copy the project files
COPY . .

CMD ["python", "aergia.py"]


