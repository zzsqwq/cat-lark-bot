package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
)

type Person struct {
	Name    string `json:"name"`
	Age     int    `json:"age"`
	Address string `json:"address"`
}

func main() {
	// 从文件中读取 JSON 数据
	jsonData, err := ioutil.ReadFile("people.json")
	if err != nil {
		panic(err)
	}

	// 将 JSON 数据转换为 Person 切片
	var people []Person
	err = json.Unmarshal(jsonData, &people)
	if err != nil {
		panic(err)
	}

	// 打印读取到的数据
	fmt.Println(people)
}
