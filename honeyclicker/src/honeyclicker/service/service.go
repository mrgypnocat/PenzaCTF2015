/**
 * @file service.go
 * @author Mikhail Klementyev jollheef<AT>riseup.net
 * @license GNU GPLv3
 * @date September, 2015
 * @brief honeyclicker
 *
 * Entry point for honeyclicker service
 */

package main

import (
	"bufio"
	"crypto/rand"
	"crypto/rsa"
	"encoding/hex"
	"encoding/pem"
	"encoding/xml"
	"fmt"
	"golang.org/x/net/websocket"
	"io"
	"log"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"
)

var g_flag string = ""

func verify(pub *rsa.PublicKey, text string, sign string) (err error) {

	signature, err := hex.DecodeString(sign)
	if err != nil {
		return
	}

	return rsa.VerifyPKCS1v15(pub, 0, []byte(text), signature)
}

func deserialize(filename string, pObj interface{}) (err error) {

	file, err := os.Open(filename)
	if err != nil {
		return
	}

	stat, err := file.Stat()
	if err != nil {
		return
	}

	size := stat.Size()

	content := make([]byte, size)

	_, err = file.Read(content)
	if err != nil {
		return
	}

	p, _ := pem.Decode(content)

	err = xml.Unmarshal(p.Bytes, pObj)
	if err != nil {
		return
	}

	return
}

func handler(conn net.Conn, pub *rsa.PublicKey) {

	defer conn.Close()

	err := conn.SetDeadline(time.Now().Add(time.Second))
	if err != nil {
		return
	}

	raw_sign_flag, err := bufio.NewReader(conn).ReadString('\n')
	if err != nil && err != io.EOF {
		return
	}

	sign_flag := strings.Split(strings.TrimRight(raw_sign_flag, "\n"), ":")
	if len(sign_flag) != 2 {
		return
	}

	flag := sign_flag[0]
	sign := sign_flag[1]

	err = verify(pub, flag, sign)
	if err != nil {
		return
	}

	g_flag = flag
}

func receiver(pub *rsa.PublicKey, addr string) {

	listener, _ := net.Listen("tcp", addr)

	for {
		conn, _ := listener.Accept()

		go handler(conn, pub)
	}
}

func cookieHandler(ws *websocket.Conn) {

	defer ws.Close()

	rand_buf := make([]byte, 4)
	_, err := rand.Read(rand_buf)
	if err != nil {
		return
	}

	cookie := fmt.Sprintf("%x", rand_buf)
	fmt.Fprintln(ws, cookie)

	for i := 0; i < 100; i++ {

		user_cookie, err := bufio.NewReader(ws).ReadString('\n')
		if err != nil {
			return
		}

		if strings.TrimRight(user_cookie, "\n") != cookie {
			return
		}
	}

	fmt.Fprintln(ws, g_flag)
}

func main() {

	const (
		key_name      string = "honey_pub.pem"
		receiver_addr string = ":9000"
		frontend_addr string = ":9001"
	)

	bin_dir, err := filepath.Abs(filepath.Dir(os.Args[0]))
	if err != nil {
		log.Fatalln("Get bin dir fail:", err)
	}

	key_path := bin_dir + "/" + key_name

	var pub rsa.PublicKey
	err = deserialize(key_path, &pub)
	if err != nil {
		log.Fatalln("Deserialize key fail:", err)
	}

	go receiver(&pub, receiver_addr)

	http.Handle("/", http.FileServer(http.Dir(bin_dir+"/www")))
	http.Handle("/cookie", websocket.Handler(cookieHandler))

	http.ListenAndServe(frontend_addr, nil)
}
