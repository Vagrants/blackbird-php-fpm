blackbird-php-fpm
===============

* Get status by using "GET /status?json"
* Please set `pm.status_path` in your php-fpm conf

```
pm.status_path = /as-you-like (default value is /status)
```

config file
-----------

| name                    | default        | type                | notes                               |
|-------------------------|----------------|---------------------|-------------------------------------|
| host                    | 127.0.0.1      | string              | frontend host                       |
| port                    | 80             | interger(1 - 65535) | frontend lisetn port                |
| timeout                 | 3              | interger(0 - 600)   | timeout for connection              |
| status_uri              | /status        | string              | sttaus uri                          |
| user                    | None           | string              | username for basic authentication   |
| password                | None           | string              | password for basic authentication   |
| ssl                     | False          | boolean             | use ssl for connection              |


Please see the "php-fpm.cfg"
