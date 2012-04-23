fibonacci-async
===============

(In)Efficient Fibonacci using recursive web requests

fibonacci-twisted
-----------------

```
fibonacci-async (master)$ python fibonacci.py
fibonacci-async (master)$ curl http://localhost:8080/13
{
    "connections": {
        "concurrent": 0, 
        "total": 1870, 
        "max_concurrent": 343
    }, 
    "message": 233
}
```
