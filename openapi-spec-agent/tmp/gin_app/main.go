// tmp/gin_app/main.go
package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()

	router.GET("/ping", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "pong",
		})
	})

	router.POST("/users", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "user created",
		})
	})

	router.GET("/users/:id", func(c *gin.Context) {
		id := c.Param("id")
		c.JSON(http.StatusOK, gin.H{
			"message": "user " + id,
		})
	})

	router.Run(":8080")
}
