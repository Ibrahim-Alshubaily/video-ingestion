package main

import (
	"log"
	"video-source/internal/capture"
)

func main() {
	if err := capture.Start(); err != nil {
		log.Fatalf("Error: %v", err)
	}
}
