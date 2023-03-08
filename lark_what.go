/*
 * MIT License
 *
 * Copyright (c) 2022 Lark Technologies Pte. Ltd.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice, shall be included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

package main

import (
	"context"
	"fmt"
	lark "github.com/larksuite/oapi-sdk-go/v3"
	larkcore "github.com/larksuite/oapi-sdk-go/v3/core"
	larkim "github.com/larksuite/oapi-sdk-go/v3/service/im/v1"
	"os"
)

func sendPostMsgUseBuilder(client *lark.Client) {
	// 第一行
	// 文本 &超链接
	zhCnPostText := &larkim.MessagePostText{Text: "第一行:", UnEscape: false}
	enUsPostText := &larkim.MessagePostText{Text: "英文内容", UnEscape: false}

	zhCnPostA := &larkim.MessagePostA{Text: "超链接", Href: "http://www.baidu.com", UnEscape: false}
	enUsPostA := &larkim.MessagePostA{Text: "link", Href: "http://www.baidu.com", UnEscape: false}

	// At人
	zhCnPostAt := &larkim.MessagePostAt{UserId: "ou_708fe07a5641ded57bbceaa72f9af08d", UserName: "战硕"}
	enCnPostAt := &larkim.MessagePostAt{UserId: "ou_708fe07a5641ded57bbceaa72f9af08d", UserName: "zhan shuo"}

	// 图片
	//zhCnPostImage := &larkim.MessagePostImage{ImageKey: "img_v2_a66c4f79-c7b5-4899-b5e3-622766c4f82g"}
	//enCnPostImage := &larkim.MessagePostImage{ImageKey: "img_v2_a66c4f79-c7b5-4899-b5e3-622766c4f82g"}

	// 第二行
	// 文本 &超链接
	zhCnPostText21 := &larkim.MessagePostText{Text: "第二行:", UnEscape: false}
	enUsPostText21 := &larkim.MessagePostText{Text: "英文内容", UnEscape: false}

	zhCnPostText22 := &larkim.MessagePostText{Text: "文本测试", UnEscape: false}
	enUsPostText22 := &larkim.MessagePostText{Text: "英文内容", UnEscape: false}

	// 图片
	//zhCnPostImage2 := &larkim.MessagePostImage{ImageKey: "img_v2_a66c4f79-c7b5-4899-b5e3-622766c4f82g"}
	//enCnPostImage2 := &larkim.MessagePostImage{ImageKey: "img_v2_a66c4f79-c7b5-4899-b5e3-622766c4f82g"}

	// 中文
	zhCn := larkim.NewMessagePostContent().
		ContentTitle("我是一个标题").
		AppendContent([]larkim.MessagePostElement{zhCnPostText, zhCnPostA, zhCnPostAt}).
		//AppendContent([]larkim.MessagePostElement{zhCnPostImage}).
		AppendContent([]larkim.MessagePostElement{zhCnPostText21, zhCnPostText22}).
		//AppendContent([]larkim.MessagePostElement{zhCnPostImage2}).
		Build()

	// 英文
	enUs := larkim.NewMessagePostContent().
		ContentTitle("im a title").
		AppendContent([]larkim.MessagePostElement{enUsPostA, enUsPostText, enCnPostAt}).
		//AppendContent([]larkim.MessagePostElement{enCnPostImage}).
		AppendContent([]larkim.MessagePostElement{enUsPostText21, enUsPostText22}).
		//AppendContent([]larkim.MessagePostElement{enCnPostImage2}).
		Build()

	// 构建消息体
	postText, err := larkim.NewMessagePost().ZhCn(zhCn).EnUs(enUs).Build()
	if err != nil {
		fmt.Println(err)
		return
	}

	resp, err := client.Im.Message.Create(context.Background(), larkim.NewCreateMessageReqBuilder().
		ReceiveIdType(larkim.ReceiveIdTypeOpenId).
		Body(larkim.NewCreateMessageReqBodyBuilder().
			MsgType(larkim.MsgTypePost).
			ReceiveId("ou_708fe07a5641ded57bbceaa72f9af08d").
			Content(postText).
			Build()).
		Build())

	if err != nil {
		fmt.Println(err)
		return
	}

	if resp.Success() {
		fmt.Println(larkcore.Prettify(resp))
		fmt.Println(*resp.Data.MessageId)
	} else {
		fmt.Println(resp.RequestId(), resp.Msg, resp.Code)
	}

}

func main() {

	var appID, appSecret = os.Getenv("APP_ID"), os.Getenv("APP_SECRET")
	client := lark.NewClient(appID, appSecret)

	// 发送文本消息
	//sendTextMsg(client)

	// 发送富文本消息
	sendPostMsgUseBuilder(client)

}
