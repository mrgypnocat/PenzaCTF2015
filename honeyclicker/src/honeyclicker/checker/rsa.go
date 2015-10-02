/**
 * @file rsa.go
 * @author Mikhail Klementyev jollheef<AT>riseup.net
 * @license GNU GPLv3
 * @date October, 2015
 * @brief rsa helpers
 *
 * Work with rsa and keys
 */

package main

import (
	"crypto/rand"
	"crypto/rsa"
	"encoding/hex"
	"encoding/pem"
	"encoding/xml"
	"os"
)

func sign(priv *rsa.PrivateKey, s string) (sign string, err error) {

	signature, err := rsa.SignPKCS1v15(rand.Reader, priv, 0, []byte(s))
	if err != nil {
		return
	}

	sign = hex.EncodeToString(signature)

	return
}

func verify(pub rsa.PublicKey, text string, sign string) (err error) {

	signature, err := hex.DecodeString(sign)
	if err != nil {
		return
	}

	return rsa.VerifyPKCS1v15(&pub, 0, []byte(text), signature)
}

func serialize(obj interface{}, preamble, filename string) (err error) {

	file, err := os.Create(filename)
	if err != nil {
		return
	}

	defer file.Close()

	serialized, err := xml.Marshal(obj)
	if err != nil {
		return
	}

	return pem.Encode(file, &pem.Block{preamble, nil, serialized})
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
