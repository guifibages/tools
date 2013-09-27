// http://stackoverflow.com/a/12756986/267777
package main

import (
	"bytes"
	"crypto/tls"
	"errors"
	"fmt"
	"log"
	"os"
	"path"
	"mime/multipart"
	"io/ioutil"

	"net/http"
	"net/http/cookiejar"
	"encoding/json"
)

func noRedirect(req *http.Request, via []*http.Request) error {
	return errors.New("No redirect allowed")
}

type AP struct {
	Clients []STALink
	wc http.Client
	address string
}
type STALink struct {
	Mac        string `json:"mac"`
	Name       string `json:"name"`
	LastIP     string `json:"lastip"`
	AssocID    float64    `json:"associd"`
	APRepeater float64    `json:"aprepeater"`
	TX         float64    `json:"tx"`
	RX         float64    `json:"rx"`
	Signal     float64    `json:"signal"`
	CCQ        float64    `json:"ccq"`
	Idle       float64    `json:"idle"`
	Uptime     float64    `json:"uptime"`
	ACK        float64    `json:"ack"`
	Distance   float64    `json:"distance"`
	TXpower    float64    `json:"txpower"`
	NoiseFloor float64    `json:"noisefloor"`
	Airmax     struct {
		Priority int `json:"priority"`
		Quality  float64 `json:"quality"`
		Beam     float64 `json:"beam"`
		Signal   float64 `json:"signal"`
		Capacity float64 `json:"capacity"`
	} `json:"airmax"`
	Stats struct {
		RX_data  float64 `json:"rx_data"`
		RX_bytes float64 `json:"rx_bytes"`
		RX_pps   float64 `json:"rx_pps"`
		TX_data  float64 `json:"tx_data"`
		TX_bytes float64 `json:"tx_bytes"`
		TX_pps   float64 `json:"tx_pps"`
	} `json:"stats"`
	Rates   []string `json:"rates"`
	Signals []float64    `json:"signals"`
}

func NewAP (address string) AP {
	var err error
	ap := new(AP)
	ap.address = address
	options := cookiejar.Options{
		PublicSuffixList: nil,
	}
	jar, err := cookiejar.New(&options)
	if err != nil {
		log.Fatal("Error creating Cookie Jar", err)
	}

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}

	loginurl := fmt.Sprintf("https://%s/login.cgi", ap.address)
	ap.wc = http.Client{tr, nil, jar}
	ap.wc.Get(loginurl)

	buf := new(bytes.Buffer)
	// Create multipart Writer for that buffer
	w := multipart.NewWriter(buf)
	// Create and write the 1st input
	if err := w.WriteField("username", "guest"); err != nil {
		log.Fatal("Error on username field")
	}
	// Create and write the 2nd input
	if err := w.WriteField("password", ""); err != nil {
		log.Fatal("Error on password field")
	}
	if err := w.WriteField("uri", "/index.cgi"); err != nil {
		log.Fatal("Error on uri field")
	}

	w.Close()
	req, err := http.NewRequest("POST", loginurl,buf)
	if err != nil {
		log.Fatal("Error creating login request", err)
	}
	req.Header.Set("Content-Type", w.FormDataContentType())
	if _, err = ap.wc.Do(req) ; err != nil {
		log.Fatal("Error sending login request", err)
	}
	return *ap

}
func (ap *AP) GetSTA() {
	staurl := fmt.Sprintf("https://%s/sta.cgi", ap.address)
	res,err := ap.wc.Get(staurl)
	if err != nil {
		log.Fatal("Error loading STA", err)
	}
	body, err := ioutil.ReadAll(res.Body)
	if err != nil {
		log.Fatal("Error reading body", err)
	}
	err = json.Unmarshal(body, &ap.Clients)
	if err != nil {
		log.Fatal("Error unmarshalling ", err)
	}
	for i := range ap.Clients {
		c := ap.Clients[i]
		fmt.Printf("%d Client: %15s   Airmax Quality: %.0f CCQ: %.0f Signal: %.2f Distance: %.1fKm\n", c.Airmax.Priority, c.Name, c.Airmax.Quality, c.CCQ, c.Signal, c.Distance/1000)
	}
}

func main() {

	if len(os.Args) != 2 {
		fmt.Printf("Usage :%s <host>\n", path.Base(os.Args[0]))
		os.Exit(1)
	}
	ap := NewAP(os.Args[1])
	ap.GetSTA()

	//fmt.Println(string(a))
	// res.Body.Close()

	/*
		resp, _ = client.Get("https://10.228.17.7/sta.cgi")

		b, _ := ioutil.ReadAll(resp.Body)
		resp.Body.Close()

		fmt.Println(string(b))
	*/
}
