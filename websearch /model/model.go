package model

import (
	"context"
	"fmt"

	openrouter "github.com/revrost/go-openrouter"
)

type Model struct {
	Name   string `json:"name"`
	ApiKey string `json:"apikey"`
	//this one should not expose with json
	Client openrouter.Client
}

// We don't need to set chat message , the reasons is this services is just for the purpose of summarie

/*
C should be the content of the website
*/
func (m *Model) Completion(c string) {
	resp, err := m.Client.CreateChatCompletion(
		context.Background(),
		openrouter.ChatCompletionRequest{
			Model: m.Name,
			Messages: []openrouter.ChatCompletionMessage{
				{
					Role:    openrouter.ChatMessageRoleSystem,
					Content: openrouter.Content{Text: "You are a good summarizer. You are given some content of a website. You have to summarize it. But don't add any extra cotnent. You job is to be a summarizer not adding ANY your own opinion even somthing you alredy know"},
				},
				{
					Role:    openrouter.ChatMessageRoleUser,
					Content: openrouter.Content{Text: "Please summarize the following content without adding any extra information. Your summarization should be within 5 lines in a total of 200 to 300 words." + c},
				},
			},
		},
	)
	if err != nil {
		panic(err)
	}

	fmt.Println(resp)
}

func NewModel(name, apikey string) (Model, error) {
	m := Model{
		Name:   name,
		ApiKey: apikey,
	}

	client := openrouter.NewClient(
		apikey,
	)
	m.Client = *client

	return m, nil
}
