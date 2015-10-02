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
	"gopkg.in/alecthomas/kingpin.v2"
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
)

const (
	honey_pub_file  string = "honey_pub.pem"
	honey_priv_file string = "honey_priv.pem"
)

func main() {

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
	}
}
