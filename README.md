# DOW-Predictor

## Current roadmap:

### Preparation phase:
- obtain data on DOW Jones EOD values
- obtain training data on financial documents
- obtain training data for current news articles
- obtain a tokenizer that utilizes named entity recognition
- obtain sentiment analysis tool

### Modules phase:
- create text summarizer for news articles
- create word embedding based on financial data

### Integration phase:
- use word embedding in neural network to predict the DOW Jones
- use linear regression on three features: previous EOD value, neural network output, sentiment
- analyze results

### Visualization phase:
- create data visualization for model
- export model to database, API, and client
