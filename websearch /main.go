package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"os"
	"strings"

	Search "github.com/JasonHKL/spy-search/search"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	_ "github.com/lib/pq"
)

var SERPER_API string
var DB *sql.DB
var OPEN_ROUTER_API string

/*
Refactor all these
*/
const (
	host     = "localhost"
	port     = 5432
	user     = "admin"
	password = "postgres"
	dbname   = "spysearch"
)

type Message struct {
	Query string `json:"query"`
}

type Result struct {
	Url     string              `json:"url"`
	Search  Search.SearchResult `json:"content"`
	Summary string              `json:"summary"`
}

func GetSearchResult(q string) (*Search.SearchResult, error) {

	url := "https://google.serper.dev/search"
	method := "POST"

	playload := strings.NewReader(`{"q":"` + q + `"}`)

	client := &http.Client{}
	req, err := http.NewRequest(method, url, playload)

	if err != nil {
		slog.Error(err.Error())
		return nil, err
	}

	req.Header.Add("X-API-KEY", SERPER_API)
	req.Header.Add("Content-Type", "application/json")

	res, err := client.Do(req)
	if err != nil {
		slog.Error(err.Error())
		return nil, err
	}

	defer res.Body.Close()
	body, err := io.ReadAll(res.Body)

	if err != nil {
		slog.Error(err.Error())
		return nil, err
	}

	var result Search.SearchResult

	err = json.Unmarshal(body, &result)
	if err != nil {
		slog.Error(err.Error())
		return nil, err
	}

	return &result, nil
}

// Connect with PSQL
func PsqlConnection() {}

/*
Add result to the database
*/
func AddSearchResult() {

}

/*
The shearch function
*/
func SearchContent(c *gin.Context) {
	/*
		Handle the search here
	*/
	var json Message
	//search query handler

	if err := c.ShouldBindJSON(&json); err != nil {
		c.JSON(400, gin.H{"error": "Invalid JSON"})
		return
	}

	res, err := GetSearchResult(json.Query)

	if err != nil {
		c.JSON(400, gin.H{"error": "Invalid JSON"})
		return
	}

	c.JSON(200, gin.H{
		"message":  json.Query,
		"resposne": res,
	})
	// POST handling
	go func() {
		//handle the res here
	}()
}

// summarize
func GetWebContent(url string) {}

// initial set up , API & DB
func Health(c *gin.Context) {
	c.JSON(200, gin.H{
		"status": true,
	})
}

func LoadDb() {
	psqlInfo := fmt.Sprintf("host=%s port=%d user=%s "+
		"password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)
	DB, err := sql.Open("postgres", psqlInfo)
	if err != nil {
		panic(err)
	}
	defer DB.Close()

	err = DB.Ping()
	if err != nil {
		panic(err)
	}
	slog.Info("Connect Successful")
}

func CloseDB() {
	DB.Close()
}

func main() {
	LoadDb()
	err := godotenv.Load()
	if err != nil {
		panic("reading API key fail")
	}
	SERPER_API = os.Getenv("SERPER_API")
	OPEN_ROUTER_API = os.Getenv("OPNE_ROUTER_API")

	router := gin.Default()
	router.GET("/health", Health)
	router.POST("/ping", SearchContent)
	router.Run()

	CloseDB()
}
