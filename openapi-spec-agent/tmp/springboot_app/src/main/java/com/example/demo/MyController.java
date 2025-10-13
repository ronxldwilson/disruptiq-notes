// tmp/springboot_app/src/main/java/com/example/demo/MyController.java
package com.example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class MyController {

    @GetMapping("/hello")
    public String hello() {
        return "Hello, Spring Boot!";
    }

    @PostMapping("/users")
    public String createUser(@RequestBody String user) {
        return "User created: " + user;
    }

    @GetMapping("/users/{id}")
    public String getUser(@PathVariable Long id) {
        return "User ID: " + id;
    }

    @PutMapping("/users/{id}")
    public String updateUser(@PathVariable Long id, @RequestBody String user) {
        return "User " + id + " updated: " + user;
    }

    @DeleteMapping("/users/{id}")
    public String deleteUser(@PathVariable Long id) {
        return "User " + id + " deleted";
    }
}
