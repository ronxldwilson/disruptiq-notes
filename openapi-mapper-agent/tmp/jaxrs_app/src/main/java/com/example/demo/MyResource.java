// tmp/jaxrs_app/src/main/java/com/example/demo/MyResource.java
package com.example.demo;

import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.PUT;
import javax.ws.rs.DELETE;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.Consumes;
import javax.ws.rs.core.MediaType;

@Path("/api/v1")
public class MyResource {

    @GET
    @Path("/hello")
    @Produces(MediaType.TEXT_PLAIN)
    public String getHello() {
        return "Hello, JAX-RS!";
    }

    @POST
    @Path("/users")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.TEXT_PLAIN)
    public String createUser(String userJson) {
        return "User created: " + userJson;
    }

    @GET
    @Path("/users/{id}")
    @Produces(MediaType.TEXT_PLAIN)
    public String getUser(@PathParam("id") String id) {
        return "User ID: " + id;
    }

    @PUT
    @Path("/users/{id}")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.TEXT_PLAIN)
    public String updateUser(@PathParam("id") String id, String userJson) {
        return "User " + id + " updated: " + userJson;
    }

    @DELETE
    @Path("/users/{id}")
    @Produces(MediaType.TEXT_PLAIN)
    public String deleteUser(@PathParam("id") String id) {
        return "User " + id + " deleted";
    }
}
