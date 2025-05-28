package main

import (
	"image-consumer/internal/capture"
	"log"
)

func main() {
	if err := capture.Start(); err != nil {
		log.Fatalf("Error: %v", err)
	}
}
