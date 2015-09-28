/*
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Mikhail Klementyev <jollheef@riseup.net>, September 2015
 */

package main

import (
	"bufio"
	"fmt"
	"io"
	"net"
	"os/exec"
	"time"
)

func tcpServer(addr string, timeout time.Duration) {

	connects := make(map[string]time.Time) // { ip : last_connect_time }

	listener, _ := net.Listen("tcp", addr)

	for {
		conn, _ := listener.Accept()

		addr := conn.RemoteAddr().String()

		ip, _, err := net.SplitHostPort(addr)
		if err != nil {
			conn.Close()
			continue
		}

		if time.Now().Before(connects[ip].Add(timeout)) {
			conn.Close()
			continue
		}

		go handler(conn)

		connects[ip] = time.Now()
	}
}

func handler(conn net.Conn) {

	err := conn.SetDeadline(time.Now().Add(10 * time.Second))
	if err != nil {
		panic(err)
	}

	defer conn.Close()

	cmd := exec.Command("./voice")
	stdin, err := cmd.StdinPipe()
	if err != nil {
		panic(err)
	}
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		panic(err)
	}
	stderr, err := cmd.StderrPipe()
	if err != nil {
		panic(err)
	}
	out := bufio.NewReader(io.MultiReader(stdout, stderr))

	cmd.Start()

	// Read header and send

	raw, _, err := out.ReadLine()
	if err != nil {
		return
	}
	fmt.Fprintf(conn, "%s\n", string(raw))

	// LOGIN:
	raw, err = out.ReadBytes(' ')
	if err != nil {
		return
	}
	fmt.Fprint(conn, string(raw))

	login, err := bufio.NewReader(conn).ReadBytes('\n')
	if err != nil {
		return
	}
	stdin.Write(login)

	// PASSWORD:
	raw, err = out.ReadBytes(' ')
	if err != nil {
		return
	}
	fmt.Fprint(conn, string(raw))

	password, err := bufio.NewReader(conn).ReadBytes('\n')
	if err != nil {
		return
	}
	stdin.Write(password)

	// COMMAND [DOWNLOAD|GENERATE]:
	raw, err = out.ReadBytes(' ')
	if err != nil {
		return
	}
	fmt.Fprint(conn, string(raw))

	raw, err = out.ReadBytes(' ')
	if err != nil {
		return
	}
	fmt.Fprint(conn, string(raw))

	command, err := bufio.NewReader(conn).ReadBytes('\n')
	if err != nil {
		return
	}
	stdin.Write(command)

	if string(command) == "DOWNLOAD\n" {

		raw, _ = out.ReadBytes(' ')
		fmt.Fprint(conn, string(raw))

	} else if string(command) == "GENERATE\n" {

		// TEXT:
		raw, err = out.ReadBytes(' ')
		if err != nil {
			return
		}
		fmt.Fprint(conn, string(raw))

		text, err := bufio.NewReader(conn).ReadBytes('\n')
		if err != nil {
			return
		}
		stdin.Write(text)

		// SUCCESS
		raw, _, err = out.ReadLine()
		if err != nil {
			return
		}
		fmt.Fprintf(conn, "%s\n", string(raw))
	}
}

func main() {
	tcpServer(":50006", time.Millisecond)
}
