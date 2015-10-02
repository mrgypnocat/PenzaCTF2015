/**
 * @file checker.go
 * @author Mikhail Klementyev jollheef<AT>riseup.net
 * @license GNU GPLv3
 * @date September, 2015
 * @brief honeyclicker checker
 *
 * Entry point for honeyclicker checker
 */

package main

import (
	"crypto/rand"
	"crypto/rsa"
	"fmt"
	"gopkg.in/alecthomas/kingpin.v2"
	"log"
	"os"
	"path/filepath"
)

type ServiceState int

const (
	// Service is online, serves the requests, stores and
	// returns flags and behaves as expected
	STATUS_UP ServiceState = iota
	// Service is online, but behaves not as expected, e.g. if HTTP server
	// listens the port, but doesn't respond on request
	STATUS_MUMBLE
	// Service is online, but past flags cannot be retrieved
	STATUS_CORRUPT
	// Service is offline
	STATUS_DOWN
	// Checker error
	STATUS_ERROR
	// Unknown
	STATUS_UNKNOWN
)

var (
	gen      = kingpin.Command("gen", "Generate key.")
	gen_bits = gen.Arg("bits", "key length").Int()

	put      = kingpin.Command("put", "put flag")
	put_host = put.Arg("host", "").String()
	put_port = put.Arg("port", "").Int()
	put_flag = put.Arg("flag", "").String()

	get       = kingpin.Command("get", "get flag")
	get_host  = get.Arg("host", "").String()
	get_port  = get.Arg("port", "").Int()
	get_state = get.Arg("state", "").String()

	chk      = kingpin.Command("chk", "check state")
	chk_host = chk.Arg("host", "").String()
	chk_port = chk.Arg("port", "").Int()
)

const (
	honey_pub_file  string = "honey_pub.pem"
	honey_priv_file string = "honey_priv.pem"
)

func readKey() *rsa.PrivateKey {

	bin_dir, err := filepath.Abs(filepath.Dir(os.Args[0]))
	if err != nil {
		log.Fatalln("Get bin dir fail:", err)
	}

	key_path := bin_dir + "/" + honey_priv_file

	var priv rsa.PrivateKey
	err = deserialize(key_path, &priv)
	if err != nil {
		log.Fatalln("Deserialize key fail:", err)
	}

	return &priv
}

func main() {

	var err error
	var status ServiceState
	var state, flag string

	switch kingpin.Parse() {
	case "gen":
		priv, err := rsa.GenerateKey(rand.Reader, 1024)
		if err != nil {
			panic(err)
		}

		err = serialize(priv, "RSA PRIVATE KEY", honey_priv_file)
		if err != nil {
			panic(err)
		}

		err = serialize(priv.PublicKey, "RSA PUBLIC KEY", honey_pub_file)
		if err != nil {
			panic(err)
		}

	case "put":
		key := readKey()
		state, status, err = svc_put(key, *put_host, *put_port, *put_flag)
		if err != nil {
			status = STATUS_DOWN
		}
		fmt.Println(state)

	case "get":
		flag, status, err = svc_get(*get_host, *get_port, *get_state)
		if err != nil {
			status = STATUS_DOWN
		}
		fmt.Println(flag)

	case "chk":
		status, err = svc_chk(*chk_host, *chk_port)
		if err != nil {
			status = STATUS_DOWN
		}
	}

	os.Exit(int(status))
}
