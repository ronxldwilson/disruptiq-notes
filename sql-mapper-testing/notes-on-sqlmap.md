# Notes on Using sqlmap

`sqlmap` is a powerful open-source penetration testing tool that automates the process of detecting and exploiting SQL injection flaws and taking over of database servers.

## Basic Testing

You can test individual endpoints by providing the URL and appropriate parameters.

### Testing a GET Endpoint

For endpoints where the parameters are in the URL (query string), you use the `-u` flag.

**Command for this project's `/user` endpoint:**
```bash
sqlmap -u "http://localhost:5000/user?id=1" --batch
```

### Testing a POST Endpoint (Form Data)

For endpoints that accept `application/x-www-form-urlencoded` data, you use the `--data` flag.

**Command for this project's `/search` endpoint:**
```bash
sqlmap -u "http://localhost:5000/search" --data="q=test" --batch
```

### Testing a POST Endpoint (JSON)

For endpoints that accept JSON data, you need to specify the `Content-Type` header and provide the JSON data.

**Command for this project's `/api/users` endpoint:**
```bash
sqlmap -u "http://localhost:5000/api/users" --data='{"email":"test@example.com"}' --headers="Content-Type: application/json" --batch
```

## Automation

### Batch Mode

The `--batch` flag runs `sqlmap` in non-interactive mode, accepting the default answers to all questions. This is useful for automated scanning.

### Crawling

`sqlmap` can crawl a website to find and test links.

```bash
sqlmap -u "http://localhost:5000" --crawl=1 --batch
```

*   `--crawl=1`: The number indicates the crawl depth.

**Limitation:** The crawler only finds links in the HTML of the pages it visits. If an endpoint is not linked from anywhere (like in this project), the crawler will not find it.

## Advanced Usage

*   **Dumping Data:** Once a vulnerability is found, you can use `sqlmap` to explore the database.
    *   `--dbs`: List databases.
    *   `--tables -D <database_name>`: List tables in a database.
    *   `--columns -T <table_name> -D <database_name>`: List columns in a table.
    *   `--dump -C <column_name> -T <table_name> -D <database_name>`: Dump data from columns.

*   **Using a Proxy:** For more complex applications, you can use a tool like [Burp Suite](https://portswigger.net/burp) or [OWASP ZAP](https://www.zaproxy.org/) to capture HTTP requests and save them to a file. You can then have `sqlmap` test all the captured requests:
    ```bash
    sqlmap -r captured_requests.txt --batch
    ```
