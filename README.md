weather-analyser
================
does stuff with weather

Functional todo
---------------

* Retrieve daily min-max forecasts (for the next 24 hours, initially)
* later on retrieve hourly forecasts to enhance the accuracy of the min-max theo
* Retrieve longer term forecasts

Technical todo
--------------
* AbstractHTTPRetriever -> AbstractRetriever
* Move protocol/method specific retrieval methods into mix-in classes and make the
  general methods in the AbstractRetriever as @abstractmethod so an impl needs
  to provide an implementation
* FTP retriever, simple http retriever, oath authenticated http retriever
