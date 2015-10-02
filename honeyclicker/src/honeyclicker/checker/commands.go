/**
 * @file commands.go
 * @author Mikhail Klementyev jollheef<AT>riseup.net
 * @license GNU GPLv3
 * @date September, 2015
 * @brief honeyclicker check functions
 *
 * Contain put,get,chk functions
 */

package main

import (
	"bufio"
	"crypto/md5"
	"crypto/rsa"
	"encoding/hex"
	"fmt"
	"golang.org/x/net/websocket"
	"io/ioutil"
	"net"
	"net/http"
)

func svc_put(key *rsa.PrivateKey, host string, port int, flag string) (
	state string, status ServiceState, err error) {

	addr := fmt.Sprintf("%s:%d", host, 9000) // another port for send flag

	conn, err := net.Dial("tcp", addr)
	if err != nil {
		status = STATUS_DOWN
		err = nil
		return
	}

	defer conn.Close()

	sign, err := sign(key, flag)
	if err != nil {
		status = STATUS_ERROR
		return
	}

	_, err = fmt.Fprintf(conn, "%s:%s", flag, sign)
	if err != nil {
		status = STATUS_MUMBLE
		err = nil
		return
	}

	return
}

func svc_get(host string, port int, state string) (
	flag string, status ServiceState, err error) {

	origin := fmt.Sprintf("http://%s:%d/", host, port)
	url := fmt.Sprintf("ws://%s:%d/cookie", host, port)

	ws, err := websocket.Dial(url, "", origin)
	if err != nil {
		status = STATUS_DOWN
		err = nil
		return
	}

	defer ws.Close()

	cred, err := bufio.NewReader(ws).ReadString('\n')
	if err != nil {
		status = STATUS_MUMBLE
		err = nil
		return
	}

	for i := 0; i < 100; i++ {
		_, err = fmt.Fprint(ws, cred)
		if err != nil {
			status = STATUS_MUMBLE
			err = nil
			return
		}
	}

	flag, err = bufio.NewReader(ws).ReadString('\n')
	if err != nil {
		status = STATUS_MUMBLE
		err = nil
		return
	}

	return
}

func svc_chk(host string, port int) (status ServiceState, err error) {

	addr := fmt.Sprintf("%s:%d", host, 9000) // another port for send flag

	conn, err := net.Dial("tcp", addr)
	if err != nil {
		status = STATUS_DOWN
		err = nil
		return
	}

	defer conn.Close()

	origin := fmt.Sprintf("http://%s:%d/", host, port)
	url := fmt.Sprintf("ws://%s:%d/cookie", host, port)

	ws, err := websocket.Dial(url, "", origin)
	if err != nil {
		status = STATUS_DOWN
		err = nil
		return
	}

	defer ws.Close()

	// Bear integrity check
	response, err := http.Get(origin)
	if err != nil {
		status = STATUS_DOWN
		err = nil
		return
	}

	defer response.Body.Close()

	contents, err := ioutil.ReadAll(response.Body)
	if err != nil {
		status = STATUS_MUMBLE
		err = nil
		return
	}

	hasher := md5.New()
	hasher.Write(contents)
	md5 := hex.EncodeToString(hasher.Sum(nil))

	if md5 != "a60532b45c4780ba5929346bf9c7a1b4" {
		status = STATUS_MUMBLE
		return
	}

	return
}
